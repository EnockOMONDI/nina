from django.contrib import admin

from .models import (
    Destination,
    Hotel,
    Package,
    PackageAvailabilityMonth,
    PackageFeature,
    PackageHotelOption,
    PackageItineraryDay,
)


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


class PackageHotelOptionInline(admin.TabularInline):
    model = PackageHotelOption
    extra = 1
    fields = (
        "hotel",
        "room_type",
        "board_basis",
        "nights",
        "price_adjustment",
        "is_recommended",
        "sort_order",
        "active",
    )
    ordering = ("-is_recommended", "sort_order", "id")


class PackageAvailabilityMonthInline(admin.TabularInline):
    model = PackageAvailabilityMonth
    extra = 1
    fields = ("month", "year", "status", "notes", "sort_order", "active")
    ordering = ("year", "month", "sort_order", "id")


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "destination",
        "category",
        "location",
        "price",
        "start_date",
        "end_date",
        "is_featured",
        "active",
        "created_at",
    )
    list_filter = ("destination", "category", "is_featured", "active", "created_at")
    search_fields = ("title", "destination__name", "location", "category", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (
        PackageFeatureInline,
        PackageItineraryDayInline,
        PackageHotelOptionInline,
        PackageAvailabilityMonthInline,
    )


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "location", "rating", "price_per_night", "active", "created_at")
    list_filter = ("rating", "active", "created_at")
    search_fields = ("name", "location", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "active", "sort_order")
    list_filter = ("active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
