import re
import zipfile
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import List, Tuple

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from xml.etree import ElementTree as ET

from adminside.models import (
    Destination,
    Hotel,
    Package,
    PackageFeature,
    PackageHotelOption,
    PackageItineraryDay,
    PackageMarketPrice,
)


NAMESPACES = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
SOURCE_DIR = Path("static/ninatours packages")

PACKAGE_IMAGE_BY_KEYWORD = [
    ("amboseli", "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?auto=format&fit=crop&w=1800&q=80"),
    ("masai mara", "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?auto=format&fit=crop&w=1800&q=80"),
    ("maasai mara", "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?auto=format&fit=crop&w=1800&q=80"),
    ("samburu", "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1800&q=80"),
    ("ol pejeta", "https://images.unsplash.com/photo-1523805009345-7448845a9e53?auto=format&fit=crop&w=1800&q=80"),
    ("taita", "https://images.unsplash.com/photo-1549366021-9f761d040a94?auto=format&fit=crop&w=1800&q=80"),
    ("north coast", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1800&q=80"),
    ("south coast", "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1800&q=80"),
    ("baobab", "https://images.unsplash.com/photo-1473116763249-2faaef81ccda?auto=format&fit=crop&w=1800&q=80"),
    ("naivasha", "https://images.unsplash.com/photo-1472396961693-142e6e269027?auto=format&fit=crop&w=1800&q=80"),
    ("nakuru", "https://images.unsplash.com/photo-1598439210625-5067c578f3f6?auto=format&fit=crop&w=1800&q=80"),
    ("elementaita", "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1800&q=80"),
]

HOTEL_IMAGE_BY_KEYWORD = [
    ("amboseli", "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?auto=format&fit=crop&w=1400&q=80"),
    ("mara", "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?auto=format&fit=crop&w=1400&q=80"),
    ("samburu", "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1400&q=80"),
    ("naivasha", "https://images.unsplash.com/photo-1472396961693-142e6e269027?auto=format&fit=crop&w=1400&q=80"),
    ("nakuru", "https://images.unsplash.com/photo-1598439210625-5067c578f3f6?auto=format&fit=crop&w=1400&q=80"),
    ("coast", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1400&q=80"),
]

DESTINATION_BY_KEYWORD = [
    ("dubai", "Dubai"),
    ("zanzibar", "Zanzibar"),
    ("maldives", "Maldives"),
    ("uganda", "Uganda"),
    ("tanzania", "Tanzania"),
    ("south africa", "South Africa"),
    ("malaysia", "Malaysia"),
]


@dataclass
class ParsedPackage:
    source_file: str
    title: str
    slug: str
    duration: str
    location: str
    category: str
    description: str
    itinerary: List[Tuple[int, str, str]]
    inclusions: str
    exclusions: str
    usd_price: Decimal | None
    kes_price: Decimal | None
    hotels: List[str]
    image_url: str
    destination_name: str


class Command(BaseCommand):
    help = "Import package docs from static/ninatours packages into Package, hotels, itinerary, and market prices."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and report, but do not write to database.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit number of files to process (0 = all).",
        )
        parser.add_argument(
            "--overwrite-images",
            action="store_true",
            help="Overwrite existing package/hotel image URLs.",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help="Skip packages whose slug already exists (import only remaining).",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]
        overwrite_images = options["overwrite_images"]
        skip_existing = options["skip_existing"]

        if not SOURCE_DIR.exists():
            self.stdout.write(self.style.ERROR(f"Folder not found: {SOURCE_DIR}"))
            return

        files = sorted(SOURCE_DIR.glob("*.docx"))
        if limit and limit > 0:
            files = files[:limit]

        if not files:
            self.stdout.write(self.style.WARNING("No .docx files found to import."))
            return

        self.stdout.write(self.style.NOTICE(f"Processing {len(files)} package document(s)..."))

        imported = 0
        skipped = 0
        failed = 0
        stats = {
            "packages_created": 0,
            "packages_updated": 0,
            "market_prices_upserted": 0,
            "hotels_created": 0,
            "hotel_options_upserted": 0,
            "itinerary_days_written": 0,
        }
        for file_path in files:
            try:
                parsed = self._parse_docx(file_path)
                if skip_existing and not dry_run and Package.objects.filter(slug=parsed.slug).exists():
                    skipped += 1
                    self.stdout.write(self.style.WARNING(f"SKIPPED existing: {parsed.source_file} ({parsed.slug})"))
                    continue
                if dry_run:
                    self._print_preview(parsed)
                else:
                    row = self._upsert_package(parsed, overwrite_images=overwrite_images)
                    for key in stats:
                        stats[key] += row.get(key, 0)
                imported += 1
            except Exception as exc:
                failed += 1
                self.stdout.write(self.style.ERROR(f"FAILED: {file_path.name} -> {exc}"))

        mode = "DRY RUN" if dry_run else "IMPORT"
        self.stdout.write(self.style.SUCCESS(f"{mode} complete. Success: {imported}, Skipped: {skipped}, Failed: {failed}"))
        if not dry_run:
            self.stdout.write(
                self.style.NOTICE(
                    "Counter Check -> "
                    f"packages created={stats['packages_created']}, "
                    f"packages updated={stats['packages_updated']}, "
                    f"market prices upserted={stats['market_prices_upserted']}, "
                    f"hotels created={stats['hotels_created']}, "
                    f"hotel options upserted={stats['hotel_options_upserted']}, "
                    f"itinerary days written={stats['itinerary_days_written']}"
                )
            )

    def _parse_docx(self, file_path: Path) -> ParsedPackage:
        with zipfile.ZipFile(file_path) as zf:
            xml_text = zf.read("word/document.xml")

        root = ET.fromstring(xml_text)
        paragraphs = []
        for p in root.findall(".//w:p", NAMESPACES):
            parts = [t.text or "" for t in p.findall(".//w:t", NAMESPACES)]
            line = "".join(parts).strip()
            if line:
                paragraphs.append(line)

        full_text = "\n".join(paragraphs)
        normalized = full_text.lower()

        title = self._extract_title(paragraphs, file_path)
        slug = slugify(title)[:220] or slugify(file_path.stem)[:220]
        duration = self._extract_duration(title, full_text)
        destination_name = self._resolve_destination(title, normalized)
        category = "Safari & Holiday"
        location = self._extract_location(title, destination_name)
        itinerary = self._extract_itinerary(paragraphs)
        inclusions, exclusions = self._extract_inclusions_exclusions(paragraphs)
        usd_price, kes_price = self._extract_prices(full_text)
        hotels = self._extract_hotels(full_text)
        image_url = self._pick_package_image(title, normalized)

        summary_items = []
        for day_num, day_title, _ in itinerary[:10]:
            summary_items.append(f"<li>Day {day_num}: {day_title}</li>")
        summary_html = "".join(summary_items) or "<li>Detailed itinerary available on request</li>"

        description = (
            "<p><strong>Safari Overview</strong></p>"
            f"<ul>{summary_html}</ul>"
        )

        return ParsedPackage(
            source_file=file_path.name,
            title=title,
            slug=slug,
            duration=duration,
            location=location,
            category=category,
            description=description,
            itinerary=itinerary,
            inclusions=inclusions,
            exclusions=exclusions,
            usd_price=usd_price,
            kes_price=kes_price,
            hotels=hotels,
            image_url=image_url,
            destination_name=destination_name,
        )

    def _extract_title(self, paragraphs: List[str], file_path: Path) -> str:
        for line in paragraphs[:20]:
            if re.search(r"\b\d+\s*DAYS?\b", line.upper()) and len(line) < 120:
                cleaned = re.split(r"Safari Overview|DAY\s*1|Validity:", line, flags=re.IGNORECASE)[0]
                cleaned = cleaned.strip(" .:-")
                if cleaned:
                    return cleaned
        stem = re.sub(r"\s*\(\d+\)\s*$", "", file_path.stem, flags=re.IGNORECASE).strip()
        return stem

    def _extract_duration(self, title: str, full_text: str) -> str:
        src = f"{title}\n{full_text}"
        day_match = re.search(r"(\d+)\s*DAYS?", src, flags=re.IGNORECASE)
        night_match = re.search(r"(\d+)\s*NIGHTS?", src, flags=re.IGNORECASE)
        if day_match and night_match:
            return f"{day_match.group(1)} Days / {night_match.group(1)} Nights"
        if day_match:
            days = int(day_match.group(1))
            nights = max(days - 1, 1)
            return f"{days} Days / {nights} Nights"
        if night_match:
            nights = int(night_match.group(1))
            return f"{nights} Nights"
        return ""

    def _resolve_destination(self, title: str, normalized_text: str) -> str:
        haystack = f"{title.lower()} {normalized_text}"
        for keyword, destination in DESTINATION_BY_KEYWORD:
            if keyword in haystack:
                return destination
        return "Kenya"

    def _extract_location(self, title: str, destination_name: str) -> str:
        upper_title = title.upper()
        if "AMBOS" in upper_title or "MARA" in upper_title or "NAIVASHA" in upper_title:
            chunks = []
            if "AMBOS" in upper_title:
                chunks.append("Amboseli")
            if "NAIVASHA" in upper_title:
                chunks.append("Naivasha")
            if "NAKURU" in upper_title:
                chunks.append("Nakuru")
            if "MARA" in upper_title:
                chunks.append("Masai Mara")
            if chunks:
                return ", ".join(chunks)
        return destination_name

    def _extract_itinerary(self, paragraphs: List[str]) -> List[Tuple[int, str, str]]:
        itinerary = []
        current = None
        in_detail_section = False
        seen_days = set()
        stop_markers = {
            "SOPA LODGES",
            "SENTRIM LODGES",
            "TOUR COST EXCLUDES",
            "SAFARI PRICE COST INCLUDES",
            "COST PER PERSON",
            "VALIDITY:",
        }

        for line in paragraphs:
            stripped = line.strip()
            up = stripped.upper()
            if "DAY - DAY" in up and "ITINERARY" in up:
                in_detail_section = True
                if current:
                    itinerary.append(current)
                    current = None
                continue
            if any(marker in up for marker in stop_markers):
                if current:
                    itinerary.append(current)
                    current = None
                continue

            if not in_detail_section:
                continue

            match = re.match(r"^\s*DAY\s*(\d+)\s*[:\-]\s*(.+)$", stripped, flags=re.IGNORECASE)
            if not match:
                match = re.match(r"^\s*DAY\s*(\d+)\s+(.+)$", stripped, flags=re.IGNORECASE)

            if match:
                day_number = int(match.group(1))
                if day_number in seen_days:
                    continue
                if current:
                    itinerary.append(current)
                    seen_days.add(current[0])
                day_title = match.group(2).strip(" -")
                current = (day_number, day_title, "")
                continue

            if current:
                day_number, day_title, day_desc = current
                addition = stripped
                day_desc = f"{day_desc} {addition}".strip() if day_desc else addition
                current = (day_number, day_title, day_desc)

        if current:
            itinerary.append(current)
            seen_days.add(current[0])

        if itinerary:
            return itinerary

        # fallback from overview bullets
        fallback = []
        for line in paragraphs:
            match = re.match(r"^\s*Day\s*(\d+)\s*[:\-]\s*(.+)$", line, flags=re.IGNORECASE)
            if match:
                fallback.append((int(match.group(1)), match.group(2).strip(), ""))
        return fallback

    def _extract_inclusions_exclusions(self, paragraphs: List[str]) -> Tuple[str, str]:
        inclusions = []
        exclusions = []
        mode = None
        for line in paragraphs:
            up = line.upper()
            if "INCLUDES" in up and ("COST" in up or "PRICE" in up):
                mode = "include"
                continue
            if "EXCLUDES" in up and "COST" in up:
                mode = "exclude"
                continue
            if mode and re.match(r"^\s*[-•]\s*(.+)$", line):
                item = re.sub(r"^\s*[-•]\s*", "", line).strip()
                if mode == "include":
                    inclusions.append(item)
                else:
                    exclusions.append(item)
            elif mode and not line.strip():
                mode = None

        return ("\n".join(inclusions), "\n".join(exclusions))

    def _extract_prices(self, full_text: str) -> Tuple[Decimal | None, Decimal | None]:
        usd_vals = []
        kes_vals = []

        for raw in re.findall(r"(?:USD|US\$)\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)", full_text, flags=re.IGNORECASE):
            val = self._to_decimal(raw)
            if val and Decimal("100") <= val <= Decimal("50000"):
                usd_vals.append(val)

        for raw in re.findall(r"(?:KES|KSHS?|KSH)\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)", full_text, flags=re.IGNORECASE):
            val = self._to_decimal(raw)
            if val and Decimal("1000") <= val <= Decimal("2000000"):
                kes_vals.append(val)

        # Fallback for docs where currency appears in heading and values are listed in tables without repeated currency labels.
        has_usd = bool(re.search(r"\bUSD\b|US\$", full_text, flags=re.IGNORECASE))
        has_kes = bool(re.search(r"\bKES\b|\bKSH\b|\bKSHS\b", full_text, flags=re.IGNORECASE))
        if not usd_vals and has_usd:
            usd_table_vals = self._extract_table_numbers_near_currency(full_text, "USD")
            if usd_table_vals:
                usd_vals.append(min(usd_table_vals))

        if not kes_vals and has_kes:
            kes_table_vals = self._extract_table_numbers_near_currency(full_text, "KES")
            if kes_table_vals:
                kes_vals.append(min(kes_table_vals))

        usd_price = min(usd_vals) if usd_vals else None
        kes_price = min(kes_vals) if kes_vals else None
        return usd_price, kes_price

    def _to_decimal(self, raw: str) -> Decimal | None:
        raw = raw.replace(",", "").strip()
        try:
            return Decimal(raw)
        except (InvalidOperation, ValueError):
            return None

    def _extract_table_numbers_near_currency(self, full_text: str, currency: str) -> List[Decimal]:
        upper = full_text.upper()
        idx = upper.find(currency.upper())
        if idx == -1:
            return []

        window = full_text[idx : idx + 5000]
        vals = []
        for raw in re.findall(r"(?<!\d)([1-9][0-9]{2,5}(?:\.[0-9]{1,2})?)(?!\d)", window):
            num = self._to_decimal(raw)
            if num is None:
                continue
            if Decimal("2010") <= num <= Decimal("2035"):
                # skip years
                continue
            if currency.upper() == "USD":
                if Decimal("300") <= num <= Decimal("50000"):
                    vals.append(num)
            else:
                if Decimal("10000") <= num <= Decimal("2000000"):
                    vals.append(num)
        return vals

    def _extract_hotels(self, full_text: str) -> List[str]:
        found = set()

        for match in re.findall(
            r"(?:overnight at|overnight accommodation.*?at)\s+([A-Za-z0-9&' .\-]+?)(?:\s+www\.|\.|,|$)",
            full_text,
            flags=re.IGNORECASE,
        ):
            candidate = self._clean_hotel_name(match)
            if candidate:
                found.add(candidate)

        for match in re.findall(r"([A-Z][A-Za-z0-9&' .\-]{2,60}(?:Lodge|Resort|Hotel|Camp|Spa))", full_text):
            candidate = self._clean_hotel_name(match)
            if candidate:
                found.add(candidate)

        return sorted(found)

    def _clean_hotel_name(self, name: str) -> str | None:
        cleaned = " ".join(name.split()).strip(" -:;,.")
        lowered = cleaned.lower()
        blocked_phrases = [
            "full day in",
            "cost per person",
            "meal plan",
            "overview",
            "gate national park",
            "nospa",
        ]
        if not cleaned or len(cleaned) < 4:
            return None
        if any(phrase in lowered for phrase in blocked_phrases):
            return None
        if not re.search(r"(lodge|resort|hotel|camp|spa)$", lowered):
            return None

        replacements = {
            "Southern Palm Beach Resort": "Southern Palms Beach Resort",
            "Penety Resort": "Penety Amboseli Resort",
            "Samburu Intrepids Tented Camp": "Samburu Intrepids Tented Camp",
        }
        return replacements.get(cleaned, cleaned)

    def _pick_package_image(self, title: str, normalized_text: str) -> str:
        haystack = f"{title.lower()} {normalized_text}"
        for keyword, url in PACKAGE_IMAGE_BY_KEYWORD:
            if keyword in haystack:
                return url
        return "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1800&q=80"

    def _pick_hotel_image(self, hotel_name: str, fallback_location: str) -> str:
        haystack = f"{hotel_name.lower()} {fallback_location.lower()}"
        for keyword, url in HOTEL_IMAGE_BY_KEYWORD:
            if keyword in haystack:
                return url
        return "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?auto=format&fit=crop&w=1400&q=80"

    @transaction.atomic
    def _upsert_package(self, parsed: ParsedPackage, overwrite_images: bool):
        row_stats = {
            "packages_created": 0,
            "packages_updated": 0,
            "market_prices_upserted": 0,
            "hotels_created": 0,
            "hotel_options_upserted": 0,
            "itinerary_days_written": 0,
        }
        destination, _ = Destination.objects.get_or_create(
            slug=slugify(parsed.destination_name),
            defaults={"name": parsed.destination_name, "active": True},
        )

        base_price = parsed.usd_price or parsed.kes_price or Decimal("0.00")

        package, package_created = Package.objects.update_or_create(
            slug=parsed.slug,
            defaults={
                "title": parsed.title,
                "duration": parsed.duration,
                "price": base_price,
                "destination": destination,
                "location": parsed.location,
                "category": parsed.category,
                "description": parsed.description,
                "inclusions": parsed.inclusions,
                "exclusions": parsed.exclusions,
                "is_featured": True,
                "active": True,
            },
        )
        if package_created:
            row_stats["packages_created"] += 1
        else:
            row_stats["packages_updated"] += 1

        if overwrite_images or not package.image_url:
            package.image_url = parsed.image_url
            package.save(update_fields=["image_url"])

        # refresh itinerary sequentially
        if parsed.itinerary:
            PackageItineraryDay.objects.filter(package=package).delete()
            for day_number, day_title, day_desc in parsed.itinerary:
                PackageItineraryDay.objects.create(
                    package=package,
                    day_number=day_number,
                    title=day_title[:200],
                    description=day_desc,
                    inclusions="",
                    exclusions="",
                    sort_order=day_number,
                )
                row_stats["itinerary_days_written"] += 1

        # create a few lightweight features from inclusions
        PackageFeature.objects.filter(package=package).delete()
        if parsed.inclusions:
            for idx, line in enumerate([ln for ln in parsed.inclusions.splitlines() if ln.strip()][:8], start=1):
                PackageFeature.objects.create(package=package, text=line[:200], sort_order=idx)

        # market prices
        if parsed.usd_price:
            PackageMarketPrice.objects.update_or_create(
                package=package,
                market=PackageMarketPrice.MARKET_INTERNATIONAL,
                defaults={
                    "currency": PackageMarketPrice.CURRENCY_USD,
                    "amount": parsed.usd_price,
                    "notes": f"Imported from {parsed.source_file}",
                    "active": True,
                    "sort_order": 2,
                },
            )
            row_stats["market_prices_upserted"] += 1
        if parsed.kes_price:
            PackageMarketPrice.objects.update_or_create(
                package=package,
                market=PackageMarketPrice.MARKET_LOCAL,
                defaults={
                    "currency": PackageMarketPrice.CURRENCY_KES,
                    "amount": parsed.kes_price,
                    "notes": f"Imported from {parsed.source_file}",
                    "active": True,
                    "sort_order": 1,
                },
            )
            row_stats["market_prices_upserted"] += 1

        # hotels and package options
        option_ids = []
        for idx, hotel_name in enumerate(parsed.hotels, start=1):
            hotel_slug = slugify(hotel_name)[:220]
            hotel, hotel_created = Hotel.objects.get_or_create(
                slug=hotel_slug,
                defaults={
                    "name": hotel_name,
                    "rating": 4,
                    "price_per_night": Decimal("0.00"),
                    "location": parsed.location or parsed.destination_name,
                    "image_url": self._pick_hotel_image(hotel_name, parsed.location or parsed.destination_name),
                    "amenities": ["Full board", "Safari access"],
                    "active": True,
                },
            )
            if hotel_created:
                row_stats["hotels_created"] += 1

            if overwrite_images or not hotel.image_url:
                hotel.image_url = self._pick_hotel_image(hotel.name, hotel.location)
                hotel.save(update_fields=["image_url"])

            option, _ = PackageHotelOption.objects.get_or_create(
                package=package,
                hotel=hotel,
                defaults={
                    "room_type": "Single / Double",
                    "board_basis": PackageHotelOption.BOARD_BASIS_FB,
                    "nights": None,
                    "price_adjustment": Decimal("0.00"),
                    "is_recommended": idx == 1,
                    "sort_order": idx,
                    "active": True,
                },
            )
            option.room_type = "Single / Double"
            option.board_basis = PackageHotelOption.BOARD_BASIS_FB
            option.sort_order = idx
            option.active = True
            option.is_recommended = idx == 1
            option.save()
            row_stats["hotel_options_upserted"] += 1
            option_ids.append(option.id)

        if option_ids:
            PackageHotelOption.objects.filter(package=package).exclude(id__in=option_ids).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported: {parsed.source_file} -> {package.title} | USD={parsed.usd_price} KES={parsed.kes_price} | Hotels={len(parsed.hotels)}"
            )
        )
        return row_stats

    def _print_preview(self, parsed: ParsedPackage):
        self.stdout.write(f"[DRY] {parsed.source_file}")
        self.stdout.write(f"      title={parsed.title}")
        self.stdout.write(f"      slug={parsed.slug}")
        self.stdout.write(f"      duration={parsed.duration}")
        self.stdout.write(f"      destination={parsed.destination_name} location={parsed.location}")
        self.stdout.write(f"      USD={parsed.usd_price} KES={parsed.kes_price}")
        self.stdout.write(f"      itinerary_days={len(parsed.itinerary)} hotels={len(parsed.hotels)}")
