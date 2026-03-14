import re
from decimal import Decimal
from django.utils.text import slugify


def normalize_hotel_name(value: str) -> str:
    normalized = (value or "").strip().lower()
    normalized = normalized.replace("&", " and ")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _image_url(name: str, city: str, region: str) -> str:
    query = ",".join([name.replace(" ", ","), city.replace(" ", ","), region.replace(" ", ","), "kenya", "hotel"])
    return f"https://source.unsplash.com/1600x900/?{query}"


CANONICAL_HOTELS = [
    {"name": "AA Lodge Amboseli", "city": "Amboseli", "region": "Kajiado", "country": "Kenya", "price_from": Decimal("220.00"), "rating": 4},
    {"name": "AA Lodge Masai Mara", "city": "Masai Mara", "region": "Narok", "country": "Kenya", "price_from": Decimal("260.00"), "rating": 4},
    {"name": "Amboseli Serena Safari Lodge", "city": "Amboseli", "region": "Kajiado", "country": "Kenya", "price_from": Decimal("340.00"), "rating": 5},
    {"name": "Amboseli Sopa", "city": "Amboseli", "region": "Kajiado", "country": "Kenya", "price_from": Decimal("290.00"), "rating": 4},
    {"name": "Amboseli Sopa Lodge", "city": "Amboseli", "region": "Kajiado", "country": "Kenya", "price_from": Decimal("300.00"), "rating": 4},
    {"name": "Amboseli Sentrim", "city": "Amboseli", "region": "Kajiado", "country": "Kenya", "price_from": Decimal("250.00"), "rating": 4},
    {"name": "Ashnil Samburu Camp", "city": "Samburu", "region": "Samburu", "country": "Kenya", "price_from": Decimal("320.00"), "rating": 4},
    {"name": "Baobab Beach Resort", "city": "Diani", "region": "Kwale", "country": "Kenya", "price_from": Decimal("210.00"), "rating": 4},
    {"name": "Baobab Beach Resort & Spa", "city": "Diani", "region": "Kwale", "country": "Kenya", "price_from": Decimal("250.00"), "rating": 5},
    {"name": "Burch's Resort", "city": "Elementaita", "region": "Nakuru", "country": "Kenya", "price_from": Decimal("120.00"), "rating": 3},
    {"name": "Diani Sea Lodge", "city": "Diani", "region": "Kwale", "country": "Kenya", "price_from": Decimal("180.00"), "rating": 4},
    {"name": "Diani Sea Resort", "city": "Diani", "region": "Kwale", "country": "Kenya", "price_from": Decimal("195.00"), "rating": 4},
    {"name": "Eleven Pearl Boutique Hotel & Spa", "city": "Diani", "region": "Kwale", "country": "Kenya", "price_from": Decimal("230.00"), "rating": 4},
    {"name": "Enashipai Resort & Spa", "city": "Naivasha", "region": "Nakuru", "country": "Kenya", "price_from": Decimal("260.00"), "rating": 5},
    {"name": "Epashikino Resort & Spa", "city": "Elementaita", "region": "Nakuru", "country": "Kenya", "price_from": Decimal("140.00"), "rating": 4},
    {"name": "Kibo Safari Camp", "city": "Amboseli", "region": "Kajiado", "country": "Kenya", "price_from": Decimal("280.00"), "rating": 4},
    {"name": "Kilaguni Serena Safari Lodge", "city": "Tsavo West", "region": "Taita Taveta", "country": "Kenya", "price_from": Decimal("360.00"), "rating": 5},
    {"name": "Lake Elementaita Serena Camp", "city": "Elementaita", "region": "Nakuru", "country": "Kenya", "price_from": Decimal("430.00"), "rating": 5},
    {"name": "Lake Naivasha Sopa Resort", "city": "Naivasha", "region": "Nakuru", "country": "Kenya", "price_from": Decimal("300.00"), "rating": 4},
    {"name": "Lake Nakuru Sopa Lodge", "city": "Nakuru", "region": "Nakuru", "country": "Kenya", "price_from": Decimal("310.00"), "rating": 4},
    {"name": "Leopard Beach Resort & Spa", "city": "Diani", "region": "Kwale", "country": "Kenya", "price_from": Decimal("270.00"), "rating": 5},
    {"name": "Mara Maisha", "city": "Masai Mara", "region": "Narok", "country": "Kenya", "price_from": Decimal("240.00"), "rating": 4},
    {"name": "Mara Serena", "city": "Masai Mara", "region": "Narok", "country": "Kenya", "price_from": Decimal("390.00"), "rating": 5},
    {"name": "Mara Simba Lodge", "city": "Masai Mara", "region": "Narok", "country": "Kenya", "price_from": Decimal("260.00"), "rating": 4},
    {"name": "Mara Sopa Lodge", "city": "Masai Mara", "region": "Narok", "country": "Kenya", "price_from": Decimal("290.00"), "rating": 4},
    {"name": "Mombasa Serena Beach", "city": "Mombasa", "region": "Mombasa", "country": "Kenya", "price_from": Decimal("310.00"), "rating": 5},
    {"name": "Naivasha Kongoni Lodge", "city": "Naivasha", "region": "Nakuru", "country": "Kenya", "price_from": Decimal("230.00"), "rating": 4},
    {"name": "North Coast Beach Hotel", "city": "Mombasa", "region": "North Coast", "country": "Kenya", "price_from": Decimal("165.00"), "rating": 3},
    {"name": "Papillon Lagoon Reef", "city": "Diani", "region": "Kwale", "country": "Kenya", "price_from": Decimal("170.00"), "rating": 4},
    {"name": "Penety Resort", "city": "Amboseli", "region": "Kajiado", "country": "Kenya", "price_from": Decimal("190.00"), "rating": 3},
    {"name": "Plaza Beach Hotel", "city": "Mombasa", "region": "North Coast", "country": "Kenya", "price_from": Decimal("160.00"), "rating": 3},
    {"name": "Prideinn Flamingo Beach Resort & Spa", "city": "Mombasa", "region": "North Coast", "country": "Kenya", "price_from": Decimal("220.00"), "rating": 4},
    {"name": "Prideinn Paradise Beach Resort & Spa", "city": "Mombasa", "region": "North Coast", "country": "Kenya", "price_from": Decimal("240.00"), "rating": 4},
    {"name": "Salt Lick Safari Lodge", "city": "Taita Hills", "region": "Taita Taveta", "country": "Kenya", "price_from": Decimal("290.00"), "rating": 4},
    {"name": "Samburu Intrepids Tented Camp", "city": "Samburu", "region": "Samburu", "country": "Kenya", "price_from": Decimal("300.00"), "rating": 4},
    {"name": "Samburu Sopa Lodge", "city": "Samburu", "region": "Samburu", "country": "Kenya", "price_from": Decimal("280.00"), "rating": 4},
    {"name": "Sarova Mara Game Camp", "city": "Masai Mara", "region": "Narok", "country": "Kenya", "price_from": Decimal("330.00"), "rating": 5},
    {"name": "Sarova Whitesands Beach Resort & Spa", "city": "Mombasa", "region": "North Coast", "country": "Kenya", "price_from": Decimal("260.00"), "rating": 5},
    {"name": "Sawela Lodge", "city": "Naivasha", "region": "Nakuru", "country": "Kenya", "price_from": Decimal("210.00"), "rating": 4},
    {"name": "Sentrim Mara", "city": "Masai Mara", "region": "Narok", "country": "Kenya", "price_from": Decimal("240.00"), "rating": 4},
    {"name": "Serena Beach Resort & Spa", "city": "Mombasa", "region": "North Coast", "country": "Kenya", "price_from": Decimal("300.00"), "rating": 5},
    {"name": "Severin Sea Lodge", "city": "Mombasa", "region": "North Coast", "country": "Kenya", "price_from": Decimal("230.00"), "rating": 4},
    {"name": "Southern Palm Beach Resort", "city": "Diani", "region": "Kwale", "country": "Kenya", "price_from": Decimal("190.00"), "rating": 4},
    {"name": "Southern Palms Beach Resort", "city": "Diani", "region": "Kwale", "country": "Kenya", "price_from": Decimal("210.00"), "rating": 4},
    {"name": "Sweetwaters Maisha Camp", "city": "Ol Pejeta", "region": "Laikipia", "country": "Kenya", "price_from": Decimal("250.00"), "rating": 4},
    {"name": "Sweetwaters Serena Camp", "city": "Ol Pejeta", "region": "Laikipia", "country": "Kenya", "price_from": Decimal("320.00"), "rating": 5},
    {"name": "Taita Hills Safari Resort & Spa", "city": "Taita Hills", "region": "Taita Taveta", "country": "Kenya", "price_from": Decimal("260.00"), "rating": 4},
    {"name": "The Maji Beach Boutique Hotel", "city": "Diani", "region": "Kwale", "country": "Kenya", "price_from": Decimal("270.00"), "rating": 5},
    {"name": "The Pelican Lodge", "city": "Elementaita", "region": "Nakuru", "country": "Kenya", "price_from": Decimal("145.00"), "rating": 3},
    {"name": "The Reef Hotel Mombasa", "city": "Mombasa", "region": "North Coast", "country": "Kenya", "price_from": Decimal("170.00"), "rating": 3},
    {"name": "Voyager Beach Resort", "city": "Mombasa", "region": "North Coast", "country": "Kenya", "price_from": Decimal("250.00"), "rating": 4},
]


ALIAS_TO_CANONICAL = {
    normalize_hotel_name("Diani Sea Reosrt"): "Diani Sea Resort",
    normalize_hotel_name("Burch’s Resort"): "Burch's Resort",
    normalize_hotel_name("Samburu Intrepids Tented Camp"): "Samburu Intrepids Tented Camp",
    normalize_hotel_name("Mara Serena"): "Mara Serena",
    normalize_hotel_name("Mombasa Serena Beach"): "Mombasa Serena Beach",
    normalize_hotel_name("Serena Beach Resort & Spa"): "Serena Beach Resort & Spa",
    normalize_hotel_name("Amboseli Sopa"): "Amboseli Sopa",
    normalize_hotel_name("Amboseli Sopa Lodge"): "Amboseli Sopa Lodge",
    normalize_hotel_name("Baobab Beach Resort"): "Baobab Beach Resort",
    normalize_hotel_name("Baobab Beach Resort & Spa"): "Baobab Beach Resort & Spa",
    normalize_hotel_name("Southern Palm Beach Resort"): "Southern Palm Beach Resort",
    normalize_hotel_name("Southern Palms Beach Resort"): "Southern Palms Beach Resort",
    normalize_hotel_name("The Reef Hotel"): "The Reef Hotel Mombasa",
    normalize_hotel_name("Oltukai"): "Amboseli Serena Safari Lodge",
}


CANONICAL_BY_NAME = {item["name"]: item for item in CANONICAL_HOTELS}
CANONICAL_SLUGS = {item["name"]: slugify(item["name"])[:220] for item in CANONICAL_HOTELS}


for item in CANONICAL_HOTELS:
    item["image_url"] = _image_url(item["name"], item["city"], item["region"])
    item.setdefault("amenities", ["Wi-Fi", "Restaurant", "Airport Transfer"])


def resolve_canonical_name(raw_name: str) -> str | None:
    normalized = normalize_hotel_name(raw_name)
    if not normalized:
        return None
    if normalized in ALIAS_TO_CANONICAL:
        return ALIAS_TO_CANONICAL[normalized]

    # exact normalized match against canonical names
    for hotel in CANONICAL_HOTELS:
        if normalize_hotel_name(hotel["name"]) == normalized:
            return hotel["name"]
    return None
