from django.core.management.base import BaseCommand
from django.utils.text import slugify

from adminside.models import Package, Hotel, PackageFeature, PackageItineraryDay


PACKAGE_DATA = [
    {
        "title": "7-Day Maasai Mara Great Migration",
        "duration": "7 Days / 6 Nights",
        "price": 2450,
        "location": "Maasai Mara, Kenya",
        "category": "Safari",
        "image_url": "https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&q=80&w=1200",
        "description": "Experience the world-renowned Great Migration in the heart of Kenya. Witness thousands of wildebeests and zebras crossing the Mara River, while predators lie in wait. This luxury safari combines high-octane wildlife action with world-class hospitality.",
        "features": ["Luxury Tented Camp", "Professional Guide", "Daily Game Drives", "Cultural Visit"],
        "itinerary": [
            {"day": 1, "title": "Arrival in Nairobi", "description": "Meet and greet at Jomo Kenyatta International Airport, transfer to your hotel for overnight stay."},
            {"day": 2, "title": "Flight to Maasai Mara", "description": "After breakfast, take a scenic flight to the Mara. Afternoon game drive begins."},
            {"day": 3, "title": "Full Day Game Drive", "description": "Explore the vast plains in search of the Big Five and witness the migration crossing."},
            {"day": 7, "title": "Departure", "description": "Morning game drive followed by a flight back to Nairobi for your international departure."},
        ],
    },
    {
        "title": "5-Day Amboseli & Tsavo Adventure",
        "duration": "5 Days / 4 Nights",
        "price": 1850,
        "location": "Amboseli, Kenya",
        "category": "Safari",
        "image_url": "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?auto=format&fit=crop&q=80&w=1200",
        "description": "View the massive herds of elephants against the backdrop of Mount Kilimanjaro and explore the red soils of Tsavo. This journey takes you through two of Kenya's most iconic landscapes.",
        "features": ["Kilimanjaro Views", "Elephant Sanctuary", "Bird Watching", "Guided Walks"],
        "itinerary": [
            {"day": 1, "title": "Nairobi to Amboseli", "description": "Drive south through the Maasai country to Amboseli National Park. Afternoon game drive."},
            {"day": 2, "title": "Amboseli Exploration", "description": "Full day in Amboseli with views of Kilimanjaro. Visit the Observation Hill for panoramic views."},
        ],
    },
    {
        "title": "Diani Beach Luxury Escape",
        "duration": "4 Days / 3 Nights",
        "price": 950,
        "location": "Diani Beach, Kenya",
        "category": "Beach",
        "image_url": "https://images.unsplash.com/photo-1533035353720-f1c6a75cd8ab?auto=format&fit=crop&q=80&w=1200",
        "description": "Relax on the pristine white sands of Diani Beach. Enjoy world-class water sports or simply soak in the Indian Ocean breeze in a private luxury villa.",
        "features": ["Beachfront Resort", "Scuba Diving", "Sunset Cruise", "Spa Treatments"],
        "itinerary": [],
    },
    {
        "title": "10-Day Great Rift Valley Expedition",
        "duration": "10 Days / 9 Nights",
        "price": 3200,
        "location": "Rift Valley, Kenya",
        "category": "Expedition",
        "image_url": "https://images.unsplash.com/photo-1523805009345-7448845a9e53?auto=format&fit=crop&q=80&w=1200",
        "description": "A comprehensive journey through the diverse landscapes of the Rift Valley, from Lake Nakuru to the shores of Lake Turkana. Discover hidden gems and ancient cultures.",
        "features": ["Flamingo Watching", "Geothermal Spas", "Off-road Adventure", "Indigenous Cultures"],
        "itinerary": [],
    },
]

HOTEL_DATA = [
    {
        "name": "Mara Serena Safari Lodge",
        "rating": 5,
        "price_per_night": 550,
        "location": "Maasai Mara",
        "image_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&q=80&w=800",
        "amenities": ["Pool", "Spa", "Restaurant", "Safari View"],
    },
    {
        "name": "Hemingways Watamu",
        "rating": 5,
        "price_per_night": 400,
        "location": "Watamu",
        "image_url": "https://images.unsplash.com/photo-1540518614846-7eded433c457?auto=format&fit=crop&q=80&w=800",
        "amenities": ["Beach Access", "Gym", "Bar", "Water Sports"],
    },
    {
        "name": "The Sarova Stanley",
        "rating": 5,
        "price_per_night": 280,
        "location": "Nairobi",
        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&q=80&w=800",
        "amenities": ["Business Center", "Rooftop Pool", "Luxury Dining"],
    },
]


class Command(BaseCommand):
    help = "Seed initial packages and hotels"

    def handle(self, *args, **options):
        for data in PACKAGE_DATA:
            slug = slugify(data["title"])
            features = data.pop("features", [])
            itinerary = data.pop("itinerary", [])
            package, _ = Package.objects.update_or_create(
                slug=slug,
                defaults={
                    **data,
                    "slug": slug,
                },
            )
            PackageFeature.objects.filter(package=package).delete()
            PackageItineraryDay.objects.filter(package=package).delete()

            for index, feature in enumerate(features, start=1):
                PackageFeature.objects.create(
                    package=package,
                    text=feature,
                    sort_order=index,
                )

            for index, item in enumerate(itinerary, start=1):
                PackageItineraryDay.objects.create(
                    package=package,
                    day_number=item.get("day", index),
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    sort_order=index,
                )

        for data in HOTEL_DATA:
            slug = slugify(data["name"])
            Hotel.objects.update_or_create(
                slug=slug,
                defaults={
                    **data,
                    "slug": slug,
                },
            )

        self.stdout.write(self.style.SUCCESS("Seeded packages and hotels."))
