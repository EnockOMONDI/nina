from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from adminside.models import (
    Destination,
    Hotel,
    Package,
    PackageAvailabilityMonth,
    PackageFeature,
    PackageHotelOption,
    PackageItineraryDay,
)


PACKAGE_TITLE = "3 Days Amboseli National Park Safari Experience"
PACKAGE_SLUG = "3-days-amboseli-national-park-safari-experience"


HOTEL_NAMES = [
    "Amboseli Serena Safari Lodge",
    "Amboseli Sopa Lodge",
    "Amboseli Sentrim Camp",
    "Penety Amboseli Resort",
    "Ol Tukai Lodge",
    "Kibo Safari Camp",
    "AA Lodge Amboseli",
]


class Command(BaseCommand):
    help = "Create/update the 3-day Amboseli 2026 package with hotel options and month availability."

    @transaction.atomic
    def handle(self, *args, **options):
        kenya_destination, _ = Destination.objects.get_or_create(
            slug="kenya",
            defaults={"name": "Kenya", "active": True, "sort_order": 1},
        )

        package, _ = Package.objects.update_or_create(
            slug=PACKAGE_SLUG,
            defaults={
                "title": PACKAGE_TITLE,
                "duration": "3 Days / 2 Nights",
                "price": Decimal("410.00"),
                "destination": kenya_destination,
                "location": "Amboseli National Park",
                "category": "Safari",
                "image_url": "https://images.unsplash.com/photo-1489392191049-fc10c97e64b6?auto=format&fit=crop&w=1800&q=80",
                "description": (
                    "<p><strong>Safari Overview</strong></p>"
                    "<ul>"
                    "<li>Day 1: Nairobi to Amboseli National Park</li>"
                    "<li>Day 2: Full day in Amboseli National Park</li>"
                    "<li>Day 3: Amboseli National Park to Nairobi</li>"
                    "</ul>"
                    "<p>Validity: January to December 2026. "
                    "Travelers: minimum 1 pax.</p>"
                ),
                "inclusions": (
                    "Transport in a pop-up roof 4 x 4 safari vehicle ideal for game viewing and photography\n"
                    "Full board accommodation while on safari\n"
                    "Accommodation in double room\n"
                    "All park entrance fees to include government taxes\n"
                    "Service of an English speaking professional driver guide\n"
                    "All game drives as detailed in the itinerary\n"
                    "Bottled water whilst on safari\n"
                    "Personalized service"
                ),
                "exclusions": (
                    "Tips\n"
                    "Laundry\n"
                    "Beverages\n"
                    "Items of a personal nature\n"
                    "Any other extras not detailed in the inclusions"
                ),
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
                "min_group_size": 1,
                "max_group_size": 6,
                "starting_price_note": (
                    "From USD 410 per person sharing (Tour Van low season, 6 pax). "
                    "Rates vary by hotel, season, vehicle, and group size."
                ),
                "is_featured": True,
                "active": True,
            },
        )

        PackageFeature.objects.filter(package=package).delete()
        for index, text in enumerate(
            [
                "Transport in pop-up roof 4x4 safari vehicle for game viewing and photography",
                "Full board accommodation (FB)",
                "Professional English-speaking driver-guide",
                "All game drives as detailed in the itinerary",
                "Park entrance fees to include government taxes",
                "Bottled water while on safari",
                "Personalized service",
                "Optional Maasai village visit (USD 30 per person)",
            ],
            start=1,
        ):
            PackageFeature.objects.create(package=package, text=text, sort_order=index)

        PackageItineraryDay.objects.filter(package=package).delete()
        PackageItineraryDay.objects.create(
            package=package,
            day_number=1,
            title="Nairobi to Amboseli National Park",
            description=(
                "Pick-up and safari briefing in Nairobi, then depart to Amboseli. "
                "Check-in and lunch, followed by an afternoon game drive with Mt. Kilimanjaro backdrop. "
                "Dinner and overnight at your hotel/lodge."
            ),
            inclusions="",
            exclusions="",
            sort_order=1,
        )
        PackageItineraryDay.objects.create(
            package=package,
            day_number=2,
            title="Full Day Game Drive in Amboseli",
            description=(
                "Full day game drive in Amboseli with excellent chances to see elephants, big cats, and birdlife. "
                "Optional Maasai village visit at extra cost."
            ),
            inclusions="",
            exclusions="",
            sort_order=2,
        )
        PackageItineraryDay.objects.create(
            package=package,
            day_number=3,
            title="Amboseli National Park to Nairobi",
            description=(
                "After breakfast and check-out, enjoy a final en-route game drive and return to Nairobi "
                "for drop-off at the agreed point."
            ),
            inclusions="",
            exclusions="",
            sort_order=3,
        )

        for month in range(1, 13):
            month_obj, _ = PackageAvailabilityMonth.objects.get_or_create(
                package=package,
                month=month,
                year=2026,
                defaults={
                    "status": PackageAvailabilityMonth.STATUS_AVAILABLE,
                    "notes": "Valid for 2026; final pricing depends on hotel option and season.",
                    "active": True,
                    "sort_order": month,
                },
            )
            month_obj.status = PackageAvailabilityMonth.STATUS_AVAILABLE
            month_obj.notes = "Valid for 2026; final pricing depends on hotel option and season."
            month_obj.active = True
            month_obj.sort_order = month
            month_obj.save()

        option_ids = []
        for index, name in enumerate(HOTEL_NAMES, start=1):
            hotel, _ = Hotel.objects.get_or_create(
                slug=slugify(name),
                defaults={
                    "name": name,
                    "rating": 4,
                    "price_per_night": Decimal("0.00"),
                    "location": "Amboseli National Park",
                    "image_url": "",
                    "amenities": ["Game drives", "Full board", "Safari access"],
                    "active": True,
                },
            )
            if not hotel.active:
                hotel.active = True
                hotel.save(update_fields=["active"])

            option, _ = PackageHotelOption.objects.get_or_create(
                package=package,
                hotel=hotel,
                defaults={
                    "room_type": "Double / Twin",
                    "board_basis": PackageHotelOption.BOARD_BASIS_FB,
                    "nights": 2,
                    "price_adjustment": Decimal("0.00"),
                    "is_recommended": index in (1, 5, 6),
                    "sort_order": index,
                    "active": True,
                },
            )
            option.room_type = "Double / Twin"
            option.board_basis = PackageHotelOption.BOARD_BASIS_FB
            option.nights = 2
            option.sort_order = index
            option.active = True
            option.is_recommended = index in (1, 5, 6)
            option.save()
            option_ids.append(option.id)

        PackageHotelOption.objects.filter(package=package).exclude(id__in=option_ids).delete()

        self.stdout.write(self.style.SUCCESS(f"Seeded package: {package.title} ({package.slug})"))
        self.stdout.write(self.style.SUCCESS(f"Hotel options: {len(option_ids)}"))
        self.stdout.write(self.style.SUCCESS("Availability months: 12 (Jan-Dec 2026)"))
