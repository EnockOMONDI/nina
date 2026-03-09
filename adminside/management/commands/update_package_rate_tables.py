import html
import re
import zipfile
from collections import deque
from pathlib import Path
from xml.etree import ElementTree as ET

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from adminside.models import Package


NAMESPACES = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
SOURCE_DIR = Path("static/ninatours packages")

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "room",
    "single",
    "double",
    "triple",
    "option",
    "cost",
    "price",
    "person",
    "per",
    "lodge",
    "lodges",
    "resort",
    "hotel",
    "camp",
    "spa",
}

HEADER_NORMALIZATIONS = (
    (
        re.compile(
            r"COST\s+PER\s+PERSON\s+SHARING\s+IN\s+A\s+DOUBLE\s+ROOM",
            flags=re.IGNORECASE,
        ),
        "COST PER PERSON SHARING",
    ),
)

SPECIAL_KEYWORDS = [
    "sopa",
    "sentrim",
    "serena",
    "prideinn",
    "baobab",
    "voyager",
    "sarova",
    "sweetwaters",
    "samburu",
    "mara",
    "naivasha",
    "nakuru",
    "amboseli",
    "coast",
]


class Command(BaseCommand):
    help = "Parse DOCX pricing tables and update PackageHotelOption.pricing_table_html for all packages."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Parse and report only; do not update DB.")
        parser.add_argument("--limit", type=int, default=0, help="Limit number of docs to process.")
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing pricing_table_html. If omitted, only empty fields are updated.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]
        overwrite = options["overwrite"]

        files = sorted(SOURCE_DIR.glob("*.docx"))
        if limit > 0:
            files = files[:limit]

        if not files:
            self.stdout.write(self.style.WARNING(f"No DOCX files found in {SOURCE_DIR}"))
            return

        self.stdout.write(self.style.NOTICE(f"Processing {len(files)} document(s) for hotel-option tables..."))

        totals = {
            "docs_processed": 0,
            "packages_found": 0,
            "packages_missing": 0,
            "options_updated": 0,
            "options_skipped_existing": 0,
            "options_fallback_all_tables": 0,
            "options_matched_by_heading": 0,
            "docs_without_tables": 0,
        }

        for doc_path in files:
            totals["docs_processed"] += 1
            try:
                title, segments = self._extract_title_and_table_segments(doc_path)
                package = self._resolve_package(title, doc_path.stem)
                if not package:
                    totals["packages_missing"] += 1
                    self.stdout.write(self.style.WARNING(f"NO PACKAGE MATCH: {doc_path.name}"))
                    continue

                totals["packages_found"] += 1
                if not segments:
                    totals["docs_without_tables"] += 1
                    self.stdout.write(self.style.WARNING(f"NO TABLES: {doc_path.name} -> {package.slug}"))
                    continue

                updated, skipped, matched, fallback = self._update_package_option_tables(
                    package=package,
                    segments=segments,
                    dry_run=dry_run,
                    overwrite=overwrite,
                )
                totals["options_updated"] += updated
                totals["options_skipped_existing"] += skipped
                totals["options_matched_by_heading"] += matched
                totals["options_fallback_all_tables"] += fallback

                mode = "DRY" if dry_run else "UPDATED"
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{mode}: {doc_path.name} -> {package.slug} | options updated={updated}, matched={matched}, fallback={fallback}, skipped={skipped}"
                    )
                )
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"FAILED: {doc_path.name} -> {exc}"))

        self.stdout.write(
            self.style.NOTICE(
                "Counter Check -> "
                f"docs={totals['docs_processed']}, "
                f"packages_found={totals['packages_found']}, "
                f"packages_missing={totals['packages_missing']}, "
                f"docs_without_tables={totals['docs_without_tables']}, "
                f"options_updated={totals['options_updated']}, "
                f"matched_by_heading={totals['options_matched_by_heading']}, "
                f"fallback_all_tables={totals['options_fallback_all_tables']}, "
                f"skipped_existing={totals['options_skipped_existing']}"
            )
        )

    def _extract_title_and_table_segments(self, doc_path: Path):
        with zipfile.ZipFile(doc_path) as zf:
            xml_text = zf.read("word/document.xml")

        root = ET.fromstring(xml_text)
        body = root.find(".//w:body", NAMESPACES)
        if body is None:
            return doc_path.stem, []

        recent_lines = deque(maxlen=8)
        segments = []
        title = None

        for child in list(body):
            if child.tag.endswith("}p"):
                text = self._paragraph_text(child).strip()
                if not text:
                    continue
                recent_lines.append(text)
                if title is None and re.search(r"\b\d+\s*DAYS?|\b\d+\s*NIGHTS?", text, flags=re.IGNORECASE):
                    cleaned = re.split(r"Safari Overview|DAY\s*1|Validity:", text, flags=re.IGNORECASE)[0].strip(" .:-")
                    if cleaned:
                        title = cleaned
            elif child.tag.endswith("}tbl"):
                rows = self._table_rows(child)
                if len(rows) < 2:
                    continue
                heading = self._pick_heading(recent_lines, len(segments) + 1)
                segments.append(
                    {
                        "heading": heading,
                        "html": self._rows_to_html_table(rows),
                        "search_blob": f"{heading} {' '.join([' '.join(r) for r in rows])}".lower(),
                    }
                )

        if not title:
            title = re.sub(r"\s*\(\d+\)\s*$", "", doc_path.stem).strip()

        return title, segments

    def _paragraph_text(self, p_elem):
        parts = []
        for t in p_elem.findall(".//w:t", NAMESPACES):
            if t.text:
                parts.append(t.text)
        return "".join(parts)

    def _table_rows(self, tbl_elem):
        rows = []
        for tr in tbl_elem.findall("./w:tr", NAMESPACES):
            cells = []
            for tc in tr.findall("./w:tc", NAMESPACES):
                text_parts = [t.text or "" for t in tc.findall(".//w:t", NAMESPACES)]
                cell = " ".join("".join(text_parts).split()).strip()
                cells.append(cell)
            if any(cells):
                rows.append(cells)
        return rows

    def _pick_heading(self, recent_lines, index):
        candidates = list(recent_lines)[::-1]
        for line in candidates:
            low = line.lower()
            if len(line) > 150:
                continue
            if any(k in low for k in ("season", "cost", "rate", "lodges", "option", "usd", "kes", "ksh")):
                return line
        return f"Rate Table {index}"

    def _rows_to_html_table(self, rows):
        col_count = max(len(r) for r in rows)
        normalized = [r + [""] * (col_count - len(r)) for r in rows]
        header = normalized[0]
        header = [self._normalize_header_cell(cell) for cell in header]
        body = normalized[1:]

        html_parts = ["<table><thead><tr>"]
        for cell in header:
            html_parts.append(f"<th>{html.escape(cell)}</th>")
        html_parts.append("</tr></thead><tbody>")
        for row in body:
            html_parts.append("<tr>")
            for cell in row:
                html_parts.append(f"<td>{html.escape(cell)}</td>")
            html_parts.append("</tr>")
        html_parts.append("</tbody></table>")
        return "".join(html_parts)

    def _normalize_header_cell(self, cell):
        normalized = cell
        for pattern, replacement in HEADER_NORMALIZATIONS:
            normalized = pattern.sub(replacement, normalized)
        return normalized

    def _resolve_package(self, title, stem):
        candidates = []
        if title:
            candidates.append(slugify(title)[:220])
        if stem:
            candidates.append(slugify(stem)[:220])
        if stem:
            candidates.append(slugify(re.sub(r"\s*-\s*2026.*$", "", stem, flags=re.IGNORECASE))[:220])

        for slug in candidates:
            if not slug:
                continue
            pkg = Package.objects.filter(slug=slug).first()
            if pkg:
                return pkg

        # fallback by loose title containment
        loose = re.sub(r"[^a-z0-9 ]", " ", (title or stem).lower())
        words = [w for w in loose.split() if len(w) > 3]
        if not words:
            return None
        qs = Package.objects.all()
        for w in words[:5]:
            qs = qs.filter(title__icontains=w)
        return qs.first()

    def _hotel_tokens(self, hotel_name):
        parts = re.findall(r"[a-z0-9]+", hotel_name.lower())
        return [p for p in parts if p not in STOPWORDS and len(p) > 2]

    def _match_segments_for_hotel(self, hotel_name, segments):
        tokens = self._hotel_tokens(hotel_name)
        h_low = hotel_name.lower()

        scored = []
        for idx, segment in enumerate(segments):
            blob = segment["search_blob"]
            score = 0
            for token in tokens:
                if token in blob:
                    score += 2
            for key in SPECIAL_KEYWORDS:
                if key in h_low and key in blob:
                    score += 4
            scored.append((score, idx))

        scored.sort(reverse=True)
        best_score = scored[0][0] if scored else 0
        if best_score <= 0:
            return [], False

        matched_indices = [idx for score, idx in scored if score >= max(3, best_score - 1)]
        matched_segments = [segments[i] for i in sorted(set(matched_indices))]
        return matched_segments, True

    @transaction.atomic
    def _update_package_option_tables(self, package, segments, dry_run=False, overwrite=False):
        updated = 0
        skipped = 0
        matched = 0
        fallback = 0

        options = list(package.hotel_options.filter(active=True).select_related("hotel"))
        if not options:
            return updated, skipped, matched, fallback

        full_html = "".join([f"<h4>{html.escape(seg['heading'])}</h4>{seg['html']}" for seg in segments])

        for option in options:
            if option.pricing_table_html and not overwrite:
                skipped += 1
                continue

            matched_segments, did_match = self._match_segments_for_hotel(option.hotel.name, segments)
            if did_match and matched_segments:
                block = "".join(
                    [f"<h4>{html.escape(seg['heading'])}</h4>{seg['html']}" for seg in matched_segments]
                )
                matched += 1
            else:
                block = full_html
                fallback += 1

            if not dry_run:
                option.pricing_table_html = block
                option.save(update_fields=["pricing_table_html"])
            updated += 1

        return updated, skipped, matched, fallback
