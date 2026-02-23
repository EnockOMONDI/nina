from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from blog.models import Category, Post


class Command(BaseCommand):
    help = "Seed initial blog categories and posts."

    def handle(self, *args, **options):
        user = get_user_model().objects.first()

        categories = [
            ("Safari Guides", "Practical safari tips and travel planning insights."),
            ("Destination Highlights", "Stories and highlights from East Africa."),
            ("Luxury Travel", "Premium stays, bespoke services, and refined experiences."),
        ]

        category_map = {}
        for title, description in categories:
            category, _ = Category.objects.get_or_create(
                title=title,
                defaults={
                    "slug": slugify(title)[:100],
                    "description": description,
                    "active": True,
                },
            )
            category_map[title] = category

        posts = [
            {
                "title": "The Great Migration: When and Where to See It",
                "excerpt": "<p>Plan your journey around the Great Migration and enjoy iconic wildlife moments.</p>",
                "content": "<p>The Great Migration is one of Africa's most breathtaking spectacles. Our team recommends...</p>",
                "category": "Safari Guides",
                "featured": True,
                "trending": True,
            },
            {
                "title": "Luxury Beach Escapes Along the Kenyan Coast",
                "excerpt": "<p>Discover serene coastlines, private villas, and curated ocean adventures.</p>",
                "content": "<p>From Diani to Watamu, the Kenyan coast offers warm waters and refined hospitality...</p>",
                "category": "Luxury Travel",
                "featured": True,
                "trending": False,
            },
            {
                "title": "Top 5 Safari Destinations for First-Time Travelers",
                "excerpt": "<p>New to safari? These destinations offer unforgettable wildlife experiences.</p>",
                "content": "<p>Maasai Mara, Amboseli, Tsavo, Samburu, and Laikipia are top choices for first-timers...</p>",
                "category": "Destination Highlights",
                "featured": False,
                "trending": True,
            },
            {
                "title": "How to Pack for a Safari: The Ziada Checklist",
                "excerpt": "<p>Pack smart with our practical checklist curated by Ziada travel experts.</p>",
                "content": "<p>Think light layers, neutral tones, and a reliable camera kit. Here is our full checklist...</p>",
                "category": "Safari Guides",
                "featured": False,
                "trending": False,
            },
        ]

        created_count = 0
        for post_data in posts:
            title = post_data["title"]
            slug = slugify(title)[:1000]
            post, created = Post.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "excerpt": post_data["excerpt"],
                    "content": post_data["content"],
                    "category": category_map.get(post_data["category"]),
                    "status": "published",
                    "featured": post_data["featured"],
                    "trending": post_data["trending"],
                    "user": user,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created_count} blog posts."))
