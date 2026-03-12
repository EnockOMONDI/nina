from django.contrib import admin

from .models import (
    CareerJob,
    Destination,
    Hotel,
    Package,
    PackageAvailabilityMonth,
    PackageFeature,
    PackageHotelOption,
    PackageItineraryDay,
    PackageMarketPrice,
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


class PackageHotelOptionInline(admin.StackedInline):
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


class PackageMarketPriceInline(admin.TabularInline):
    model = PackageMarketPrice
    extra = 1
    fields = ("market", "currency", "amount", "notes", "sort_order", "active")
    ordering = ("sort_order", "id")


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    fields = (
        "title",
        "slug",
        "duration",
        "price",
        "destination",
        "location",
        "category",
        "image_url",
        "description",
        "pricing_table_html",
        "inclusions",
        "exclusions",
        "start_date",
        "end_date",
        "min_group_size",
        "max_group_size",
        "starting_price_note",
        "is_featured",
        "active",
    )
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
        PackageMarketPriceInline,
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


@admin.register(CareerJob)
class CareerJobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "department",
        "location",
        "job_type",
        "status",
        "posted_on",
        "deadline",
        "active",
    )
    list_filter = ("job_type", "status", "active", "department", "posted_on", "deadline")
    search_fields = ("title", "department", "location", "slug")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("sort_order", "-created_at")


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "active", "sort_order")
    list_filter = ("active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
