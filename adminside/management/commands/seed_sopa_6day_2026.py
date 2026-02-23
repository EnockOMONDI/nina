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


PACKAGE_TITLE = "6 Days Sopa Lodges Amboseli, Naivasha & Mara"
PACKAGE_SLUG = "6-days-sopa-lodges-amboseli-naivasha-mara-2026"

HOTEL_NAMES = [
    "Amboseli Sopa Lodge",
    "Lake Naivasha Sopa Resort",
    "Mara Sopa Lodge",
]


class Command(BaseCommand):
    help = "Create/update the 6-day Sopa circuit package and ensure linked hotels exist."

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
                "duration": "6 Days / 5 Nights",
                "price": Decimal("1275.00"),
                "destination": kenya_destination,
                "location": "Amboseli, Naivasha & Maasai Mara",
                "category": "Safari Circuit",
                "image_url": "https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&w=1800&q=80",
                "description": (
                    "<p><strong>Safari Overview</strong></p>"
                    "<ul>"
                    "<li>Day 1: Nairobi to Amboseli National Park</li>"
                    "<li>Day 2: Full day in Amboseli National Park</li>"
                    "<li>Day 3: Amboseli National Park to Lake Naivasha</li>"
                    "<li>Day 4: Lake Naivasha to Maasai Mara</li>"
                    "<li>Day 5: Full day in Maasai Mara</li>"
                    "<li>Day 6: Maasai Mara to Nairobi</li>"
                    "</ul>"
                    "<p>Validity: 01 Jan 2026 to 01 Jan 2027.</p>"
                ),
                "inclusions": (
                    "Transport in a pop-up roof 4 x 4 Land Cruiser safari vehicle ideal for game viewing and photography\n"
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
                    "Any other extras not detailed in inclusions\n"
                    "Seasonal supplements where applicable"
                ),
                "start_date": "2026-01-01",
                "end_date": "2027-01-01",
                "min_group_size": 1,
                "max_group_size": 6,
                "starting_price_note": (
                    "From USD 1,275 per person sharing (Tour Van, Green Season, 6 pax). "
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
                "Pickup and safari briefing in Nairobi, then transfer to Amboseli. Check-in and lunch, followed by an afternoon game drive with Mount Kilimanjaro views. Dinner and overnight at Amboseli Sopa Lodge.",
            ),
            (
                2,
                "Full Day Game Drive in Amboseli",
                "Full-day game drive in Amboseli with chances to see elephants, big cats and over 400 bird species. Optional Maasai village visit at extra cost. Dinner and overnight at Amboseli Sopa Lodge.",
            ),
            (
                3,
                "Amboseli National Park to Lake Naivasha",
                "Morning breakfast and checkout with an en-route game drive, then proceed to Lake Naivasha. Afternoon visit to Hell's Gate National Park and optional boat ride at extra cost. Dinner and overnight at Lake Naivasha Sopa Resort.",
            ),
            (
                4,
                "Lake Naivasha to Maasai Mara National Reserve",
                "Breakfast and transfer to Maasai Mara with arrival for lunch. Afternoon game drive across wildlife-rich zones with high chances of spotting big cats and the Big Five. Dinner and overnight at Mara Sopa Lodge.",
            ),
            (
                5,
                "Full Day Game Drive in Maasai Mara",
                "Early breakfast and full-day game drive. During migration months (Jul-Oct), witness wildebeest crossings and predator action. Picnic or lodge lunch, then continue evening game viewing. Dinner and overnight at Mara Sopa Lodge.",
            ),
            (
                6,
                "Maasai Mara to Nairobi",
                "Breakfast, checkout, and final en-route game drive before returning to Nairobi for drop-off at the agreed point.",
            ),
        ]
        for day_number, title, description in itinerary:
            PackageItineraryDay.objects.create(
                package=package,
                day_number=day_number,
                title=title,
                description=description,
                inclusions="",
                exclusions="",
                sort_order=day_number,
            )

        for month in range(1, 13):
            month_obj, _ = PackageAvailabilityMonth.objects.get_or_create(
                package=package,
                month=month,
                year=2026,
                defaults={
                    "status": PackageAvailabilityMonth.STATUS_AVAILABLE,
                    "notes": "Valid season; final rates depend on travel season and vehicle option.",
                    "active": True,
                    "sort_order": month,
                },
            )
            month_obj.status = PackageAvailabilityMonth.STATUS_AVAILABLE
            month_obj.notes = "Valid season; final rates depend on travel season and vehicle option."
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
            option.price_adjustment = Decimal("0.00")
            option.is_recommended = True
            option.sort_order = index
            option.active = True
            option.save()
            option_ids.append(option.id)

        PackageHotelOption.objects.filter(package=package).exclude(id__in=option_ids).delete()

        self.stdout.write(self.style.SUCCESS(f"Seeded package: {package.title} ({package.slug})"))
        self.stdout.write(self.style.SUCCESS(f"Hotels linked: {len(option_ids)}"))
        self.stdout.write(self.style.SUCCESS("Availability months: Jan-Dec 2026 + Jan 2027"))
