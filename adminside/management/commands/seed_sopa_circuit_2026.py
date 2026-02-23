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


PACKAGE_TITLE = "7 Days Sopa Lodges Amboseli, Naivasha, Nakuru & Mara"
PACKAGE_SLUG = "7-days-sopa-lodges-amboseli-naivasha-nakuru-mara-2026"

HOTEL_NAMES = [
    "Amboseli Sopa Lodge",
    "Lake Naivasha Sopa Resort",
    "Mara Sopa Lodge",
    "Lake Nakuru Sopa Lodge",
]


class Command(BaseCommand):
    help = "Create/update the 7-day Sopa circuit package and link all included hotels."

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
                "duration": "7 Days / 6 Nights",
                "price": Decimal("1485.00"),
                "destination": kenya_destination,
                "location": "Amboseli, Naivasha, Nakuru & Maasai Mara",
                "category": "Safari Circuit",
                "image_url": "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?auto=format&fit=crop&w=1800&q=80",
                "description": (
                    "<p><strong>Safari Overview</strong></p>"
                    "<ul>"
                    "<li>Day 1: Nairobi to Amboseli National Park</li>"
                    "<li>Day 2: Full day in Amboseli National Park</li>"
                    "<li>Day 3: Amboseli to Lake Naivasha</li>"
                    "<li>Day 4: Lake Naivasha to Maasai Mara</li>"
                    "<li>Day 5: Full day in Maasai Mara</li>"
                    "<li>Day 6: Maasai Mara to Lake Nakuru</li>"
                    "<li>Day 7: Lake Nakuru to Nairobi</li>"
                    "</ul>"
                    "<p>Validity: 01 Jan 2026 to 01 Jan 2027.</p>"
                ),
                "start_date": "2026-01-01",
                "end_date": "2027-01-01",
                "min_group_size": 1,
                "max_group_size": 6,
                "starting_price_note": (
                    "From USD 1,485 per person sharing (Tour Van, Green Season, 6 pax). "
                    "Rates vary by season, vehicle option, and group size."
                ),
                "is_featured": True,
                "active": True,
            },
        )

        PackageFeature.objects.filter(package=package).delete()
        for index, text in enumerate(
            [
                "Transport in a pop-up roof 4x4 safari vehicle ideal for game viewing",
                "Full board accommodation while on safari",
                "All park entrance fees including government taxes",
                "English-speaking professional driver guide",
                "All game drives as per itinerary",
                "Bottled water while on safari",
                "Great Rift Valley viewpoint stopover",
                "Optional Maasai village visit (USD 30 per person)",
                "Optional Lake Naivasha boat ride (USD 30 per person)",
            ],
            start=1,
        ):
            PackageFeature.objects.create(package=package, text=text, sort_order=index)

        PackageItineraryDay.objects.filter(package=package).delete()
        itinerary = [
            (
                1,
                "Nairobi to Amboseli National Park",
                "Departure from Nairobi, check-in and lunch, afternoon game drive in Amboseli, dinner and overnight at Amboseli Sopa Lodge.",
            ),
            (
                2,
                "Full Day in Amboseli National Park",
                "Full-day game drive with chances to see elephants, big cats and diverse birdlife. Overnight at Amboseli Sopa Lodge.",
            ),
            (
                3,
                "Amboseli to Lake Naivasha",
                "En-route game drive and transfer to Lake Naivasha with a Great Rift Valley viewpoint stop. Visit Hell's Gate; optional boat ride on the lake.",
            ),
            (
                4,
                "Lake Naivasha to Maasai Mara",
                "Transfer to Maasai Mara, check-in and lunch, afternoon game drive and overnight at Mara Sopa Lodge.",
            ),
            (
                5,
                "Full Day in Maasai Mara",
                "Extended game drives in the reserve with optional hot air balloon and bush experiences.",
            ),
            (
                6,
                "Maasai Mara to Lake Nakuru",
                "Transfer to Lake Nakuru National Park, afternoon game drive with flamingos, rhinos and birdlife, overnight at Lake Nakuru Sopa Lodge.",
            ),
            (
                7,
                "Lake Nakuru to Nairobi",
                "Breakfast, check-out, and return transfer to Nairobi for drop-off.",
            ),
        ]
        for sort_order, title, description in itinerary:
            PackageItineraryDay.objects.create(
                package=package,
                day_number=sort_order,
                title=title,
                description=description,
                inclusions="Accommodation, transport, game drives, and meals as per plan.",
                exclusions="Tips, laundry, beverages, personal items, and extra optional activities.",
                sort_order=sort_order,
            )

        # Availability: full 2026 plus early Jan 2027 validity end window.
        for month in range(1, 13):
            month_obj, _ = PackageAvailabilityMonth.objects.get_or_create(
                package=package,
                month=month,
                year=2026,
                defaults={
                    "status": PackageAvailabilityMonth.STATUS_AVAILABLE,
                    "notes": "Valid package season; final rates depend on season and vehicle type.",
                    "active": True,
                    "sort_order": month,
                },
            )
            month_obj.status = PackageAvailabilityMonth.STATUS_AVAILABLE
            month_obj.notes = "Valid package season; final rates depend on season and vehicle type."
            month_obj.active = True
            month_obj.sort_order = month
            month_obj.save()

        jan_2027, _ = PackageAvailabilityMonth.objects.get_or_create(
            package=package,
            month=1,
            year=2027,
            defaults={
                "status": PackageAvailabilityMonth.STATUS_AVAILABLE,
                "notes": "Validity extends to 01 Jan 2027.",
                "active": True,
                "sort_order": 13,
            },
        )
        jan_2027.status = PackageAvailabilityMonth.STATUS_AVAILABLE
        jan_2027.notes = "Validity extends to 01 Jan 2027."
        jan_2027.active = True
        jan_2027.sort_order = 13
        jan_2027.save()

        option_ids = []
        for index, name in enumerate(HOTEL_NAMES, start=1):
            hotel_location = "Kenya"
            if "Amboseli" in name:
                hotel_location = "Amboseli National Park"
            elif "Naivasha" in name:
                hotel_location = "Lake Naivasha"
            elif "Nakuru" in name:
                hotel_location = "Lake Nakuru"
            elif "Mara" in name:
                hotel_location = "Maasai Mara"

            hotel, _ = Hotel.objects.get_or_create(
                slug=slugify(name),
                defaults={
                    "name": name,
                    "rating": 4,
                    "price_per_night": Decimal("0.00"),
                    "location": hotel_location,
                    "image_url": "",
                    "amenities": ["Full board", "Game drive access", "Nature views"],
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
                    "room_type": "Single / Double",
                    "board_basis": PackageHotelOption.BOARD_BASIS_FB,
                    "nights": 1,
                    "price_adjustment": Decimal("0.00"),
                    "is_recommended": True,
                    "sort_order": index,
                    "active": True,
                },
            )
            option.room_type = "Single / Double"
            option.board_basis = PackageHotelOption.BOARD_BASIS_FB
            option.nights = 1
            option.sort_order = index
            option.active = True
            option.is_recommended = True
            option.save()
            option_ids.append(option.id)

        PackageHotelOption.objects.filter(package=package).exclude(id__in=option_ids).delete()

        self.stdout.write(self.style.SUCCESS(f"Seeded package: {package.title} ({package.slug})"))
        self.stdout.write(self.style.SUCCESS(f"Hotels linked: {len(option_ids)}"))
        self.stdout.write(self.style.SUCCESS("Availability months: Jan-Dec 2026 + Jan 2027"))
