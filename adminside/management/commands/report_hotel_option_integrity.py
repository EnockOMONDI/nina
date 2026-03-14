from django.core.management.base import BaseCommand

from adminside.models import Package, PackageHotelOption


class Command(BaseCommand):
    help = "Report package hotel option integrity after staging/remap."

    def handle(self, *args, **options):
        total = PackageHotelOption.objects.count()
        active_options = PackageHotelOption.objects.filter(active=True).count()
        inactive_linked = PackageHotelOption.objects.filter(hotel__active=False).count()
        active_linked = PackageHotelOption.objects.filter(hotel__active=True).count()

        self.stdout.write(self.style.NOTICE("Hotel option integrity report:"))
        self.stdout.write(f"  - total options: {total}")
        self.stdout.write(f"  - active options: {active_options}")
        self.stdout.write(f"  - linked to active hotels: {active_linked}")
        self.stdout.write(f"  - linked to inactive hotels: {inactive_linked}")

        missing_active = []
        for pkg in Package.objects.filter(active=True).order_by("title"):
            active_count = pkg.hotel_options.filter(active=True, hotel__active=True).count()
            any_count = pkg.hotel_options.filter(active=True).count()
            if any_count > 0 and active_count == 0:
                missing_active.append((pkg.id, pkg.title, any_count))

        self.stdout.write(f"  - packages with active options but none linked to active hotel: {len(missing_active)}")
        for pkg_id, title, count in missing_active[:100]:
            self.stdout.write(f"    * package_id={pkg_id} title='{title}' active_options={count}")
