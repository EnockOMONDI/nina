import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from adminside.hotel_catalog import resolve_canonical_name
from adminside.models import Hotel, PackageHotelOption


class Command(BaseCommand):
    help = "Remap package hotel options to active canonical hotels using exact/alias/manual overrides."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Write remap updates.")
        parser.add_argument(
            "--overrides-csv",
            default="",
            help="Optional CSV with columns old_name,canonical_name",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        overrides = self._load_overrides(options["overrides_csv"])

        canonical_hotels = {
            h.name: h
            for h in Hotel.objects.filter(active=True)
        }
        canonical_by_slug = {slugify(name)[:220]: name for name in canonical_hotels.keys()}

        if not canonical_hotels:
            raise CommandError("No active hotels found. Run stage_canonical_hotels --mode apply first.")

        options_qs = PackageHotelOption.objects.select_related("hotel", "package").order_by("id")

        remap_plan = []
        unresolved = []
        for option in options_qs:
            source_hotel = option.hotel
            if source_hotel.active:
                continue

            target_name = None
            if source_hotel.name in overrides:
                target_name = overrides[source_hotel.name]
            else:
                target_name = resolve_canonical_name(source_hotel.name)

            if not target_name:
                slug_guess = slugify(source_hotel.name)[:220]
                target_name = canonical_by_slug.get(slug_guess)

            target_hotel = canonical_hotels.get(target_name) if target_name else None
            if not target_hotel:
                unresolved.append(option)
                continue

            remap_plan.append((option, target_hotel))

        self.stdout.write(self.style.NOTICE("Remap summary:"))
        self.stdout.write(f"  - inactive-linked options: {len(remap_plan) + len(unresolved)}")
        self.stdout.write(f"  - mapped: {len(remap_plan)}")
        self.stdout.write(f"  - unresolved: {len(unresolved)}")

        if unresolved:
            self.stdout.write(self.style.WARNING("Unresolved options:"))
            for option in unresolved[:100]:
                self.stdout.write(
                    f"  - option_id={option.id} package='{option.package.title}' hotel='{option.hotel.name}'"
                )

        if not apply_changes:
            self.stdout.write(self.style.NOTICE("Dry run complete. Re-run with --apply to write updates."))
            return

        if unresolved:
            raise CommandError("Unresolved mappings present. Add --overrides-csv and retry.")

        with transaction.atomic():
            for option, target_hotel in remap_plan:
                option.hotel = target_hotel
                option.save(update_fields=["hotel"])

        still_inactive = PackageHotelOption.objects.filter(hotel__active=False).count()
        self.stdout.write(self.style.SUCCESS("Package hotel option remap applied."))
        self.stdout.write(f"  - remaining options linked to inactive hotels: {still_inactive}")

    def _load_overrides(self, path_str: str):
        if not path_str:
            return {}

        path = Path(path_str)
        if not path.exists():
            raise CommandError(f"Overrides CSV not found: {path}")

        mapping = {}
        with path.open("r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            required = {"old_name", "canonical_name"}
            if not required.issubset(set(reader.fieldnames or [])):
                raise CommandError("Overrides CSV must include old_name,canonical_name columns")
            for row in reader:
                old_name = (row.get("old_name") or "").strip()
                canonical_name = (row.get("canonical_name") or "").strip()
                if old_name and canonical_name:
                    mapping[old_name] = canonical_name
        return mapping
