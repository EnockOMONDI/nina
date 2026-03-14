from collections import defaultdict
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from adminside.hotel_catalog import ALIAS_TO_CANONICAL, CANONICAL_HOTELS
from adminside.models import Hotel


class Command(BaseCommand):
    help = "Inactive-first staging for canonical hotels (dry-run/apply/report)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode",
            choices=["dry-run", "apply", "report"],
            default="dry-run",
            help="Operation mode.",
        )

    def handle(self, *args, **options):
        mode = options["mode"]
        if mode == "report":
            self._report()
            return

        alias_collisions = self._alias_collisions()
        if alias_collisions:
            self.stdout.write(self.style.WARNING("Alias collisions detected:"))
            for key, names in alias_collisions.items():
                self.stdout.write(f"  - {key}: {', '.join(sorted(names))}")

        self._stage(mode == "apply")

    def _alias_collisions(self):
        reverse = defaultdict(set)
        for alias, canonical in ALIAS_TO_CANONICAL.items():
            reverse[alias].add(canonical)
        return {k: v for k, v in reverse.items() if len(v) > 1}

    def _report(self):
        total = Hotel.objects.count()
        active = Hotel.objects.filter(active=True).count()
        inactive = Hotel.objects.filter(active=False).count()
        self.stdout.write(self.style.NOTICE(f"Hotels total={total} active={active} inactive={inactive}"))

        by_region = defaultdict(int)
        for region in Hotel.objects.filter(active=True).values_list("region", flat=True):
            by_region[(region or "(none)")] += 1

        self.stdout.write(self.style.NOTICE("Active hotels by region:"))
        for region, count in sorted(by_region.items()):
            self.stdout.write(f"  - {region}: {count}")

    def _stage(self, apply_changes: bool):
        existing_total = Hotel.objects.count()
        existing_active = Hotel.objects.filter(active=True).count()
        canonical_names = {row["name"] for row in CANONICAL_HOTELS}

        to_create = 0
        to_update = 0
        for row in CANONICAL_HOTELS:
            slug = slugify(row["name"])[:220]
            existing = Hotel.objects.filter(slug=slug).first()
            if existing:
                to_update += 1
            else:
                to_create += 1

        self.stdout.write(self.style.NOTICE("Staging summary:"))
        self.stdout.write(f"  - mode: {'apply' if apply_changes else 'dry-run'}")
        self.stdout.write(f"  - existing hotels: {existing_total} (active={existing_active})")
        self.stdout.write(f"  - canonical set: {len(CANONICAL_HOTELS)}")
        self.stdout.write(f"  - canonical create: {to_create}")
        self.stdout.write(f"  - canonical update: {to_update}")

        if not apply_changes:
            return

        with transaction.atomic():
            Hotel.objects.update(active=False)

            for row in CANONICAL_HOTELS:
                slug = slugify(row["name"])[:220]
                defaults = {
                    "name": row["name"],
                    "city": row["city"],
                    "region": row["region"],
                    "country": row["country"],
                    "location": row["city"] or row["region"] or row["country"],
                    "image_url": row["image_url"],
                    "price_per_night": row["price_from"],
                    "rating": row.get("rating", 4),
                    "amenities": row.get("amenities", []),
                    "active": True,
                }
                Hotel.objects.update_or_create(slug=slug, defaults=defaults)

        now_active = Hotel.objects.filter(active=True).count()
        now_inactive = Hotel.objects.filter(active=False).count()

        self.stdout.write(self.style.SUCCESS("Canonical staging applied."))
        self.stdout.write(f"  - active hotels: {now_active}")
        self.stdout.write(f"  - inactive hotels: {now_inactive}")

        missing = canonical_names - set(Hotel.objects.filter(active=True).values_list("name", flat=True))
        if missing:
            self.stdout.write(self.style.WARNING(f"Missing canonical rows: {sorted(missing)}"))
