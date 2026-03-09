import re

from django.core.management.base import BaseCommand

from adminside.models import PackageHotelOption


HEADER_NORMALIZATIONS = (
    (
        re.compile(
            r"COST\s+PER\s+PERSON\s+SHARING\s+IN\s+A\s+DOUBLE\s+ROOM",
            flags=re.IGNORECASE,
        ),
        "COST PER PERSON SHARING",
    ),
)


class Command(BaseCommand):
    help = "Normalize table header text stored in PackageHotelOption.pricing_table_html."

    def handle(self, *args, **options):
        checked = 0
        updated = 0

        queryset = PackageHotelOption.objects.exclude(pricing_table_html="")
        for option in queryset.iterator():
            checked += 1
            original = option.pricing_table_html
            normalized = original

            for pattern, replacement in HEADER_NORMALIZATIONS:
                normalized = pattern.sub(replacement, normalized)

            if normalized != original:
                option.pricing_table_html = normalized
                option.save(update_fields=["pricing_table_html"])
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"checked={checked} updated={updated}"))
