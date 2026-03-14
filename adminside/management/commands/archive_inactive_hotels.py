import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from adminside.models import Hotel


class Command(BaseCommand):
    help = "Export inactive hotels to CSV and optionally delete them."

    def add_arguments(self, parser):
        parser.add_argument("--output", default="inactive_hotels_archive.csv")
        parser.add_argument("--delete", action="store_true", help="Delete inactive hotels after export.")

    def handle(self, *args, **options):
        output_path = Path(options["output"])
        delete_rows = options["delete"]

        rows = list(Hotel.objects.filter(active=False).order_by("id"))
        with output_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow([
                "id",
                "name",
                "slug",
                "city",
                "region",
                "country",
                "location",
                "price_per_night",
                "rating",
                "image_url",
                "created_at",
                "updated_at",
            ])
            for row in rows:
                writer.writerow([
                    row.id,
                    row.name,
                    row.slug,
                    row.city,
                    row.region,
                    row.country,
                    row.location,
                    row.price_per_night,
                    row.rating,
                    row.image_url,
                    row.created_at,
                    row.updated_at,
                ])

        self.stdout.write(self.style.SUCCESS(f"Archived {len(rows)} inactive hotels -> {output_path}"))

        if delete_rows:
            deleted, _ = Hotel.objects.filter(active=False).delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted rows: {deleted}"))
