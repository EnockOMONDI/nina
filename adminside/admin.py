from django.contrib import admin

from .models import Package, Hotel, PackageFeature, PackageItineraryDay


class PackageFeatureInline(admin.TabularInline):
    model = PackageFeature
    extra = 1
    fields = ("text", "sort_order")
    ordering = ("sort_order", "id")


class PackageItineraryDayInline(admin.StackedInline):
    model = PackageItineraryDay
    extra = 1
    fields = ("day_number", "title", "description", "inclusions", "exclusions", "sort_order")
    ordering = ("sort_order", "day_number", "id")


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "category", "location", "price", "is_featured", "active", "created_at")
    list_filter = ("category", "is_featured", "active", "created_at")
    search_fields = ("title", "location", "category", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (PackageFeatureInline, PackageItineraryDayInline)


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "location", "rating", "price_per_night", "active", "created_at")
    list_filter = ("rating", "active", "created_at")
    search_fields = ("name", "location", "slug")
    prepopulated_fields = {"slug": ("name",)}
