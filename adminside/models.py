from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


class Package(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    duration = models.CharField(max_length=100, blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    location = models.CharField(max_length=150, blank=True, default="")
    category = models.CharField(max_length=100, blank=True, default="")
    image_url = models.URLField(blank=True, default="")
    description = CKEditor5Field(config_name="default", blank=True, default="")
    is_featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PackageFeature(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="feature_items")
    text = models.CharField(max_length=200)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.package.title} - {self.text}"


class PackageItineraryDay(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="itinerary_days")
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    inclusions = models.TextField(blank=True, default="")
    exclusions = models.TextField(blank=True, default="")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "day_number", "id"]

    def __str__(self):
        return f"{self.package.title} - Day {self.day_number}: {self.title}"


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    rating = models.PositiveSmallIntegerField(default=0)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    location = models.CharField(max_length=150, blank=True, default="")
    image_url = models.URLField(blank=True, default="")
    amenities = models.JSONField(default=list, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:220]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
