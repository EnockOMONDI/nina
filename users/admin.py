from django.contrib import admin
from django.utils.html import format_html

from .models import (
    CareerApplication,
    ContactInquiry,
    CorporateInquiry,
    HotelInquiry,
    MICEInquiry,
    StudentTravelInquiry,
    NGOTravelInquiry,
    PackageQuoteInquiry,
    TripFeedback,
)


class ReadAwareAdmin(admin.ModelAdmin):
    actions = ("mark_as_read", "mark_as_unread")

    @admin.display(description="Unread")
    def unread_badge(self, obj):
        if getattr(obj, "is_read", False):
            return format_html('<span style="color:#64748b;font-weight:700;">No</span>')
        return format_html(
            '<span style="background:#da176e;color:#fff;border-radius:999px;padding:2px 8px;font-size:11px;font-weight:800;">NEW</span>'
        )

    @admin.action(description="Mark selected as read")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Mark selected as unread")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        model = self.model
        model.objects.filter(pk=object_id, is_read=False).update(is_read=True)
        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)


@admin.register(ContactInquiry)
class ContactInquiryAdmin(ReadAwareAdmin):
    list_display = ("unread_badge", "full_name", "email", "subject", "is_resolved", "created_at")
    list_filter = ("is_read", "is_resolved", "created_at")
    search_fields = ("full_name", "email", "subject")


@admin.register(MICEInquiry)
class MICEInquiryAdmin(ReadAwareAdmin):
    list_display = ("unread_badge", "company_name", "contact_person", "email", "event_type", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("company_name", "contact_person", "email")


@admin.register(StudentTravelInquiry)
class StudentTravelInquiryAdmin(ReadAwareAdmin):
    list_display = ("unread_badge", "school_name", "contact_person", "email", "program_stage", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("school_name", "contact_person", "email")


@admin.register(NGOTravelInquiry)
class NGOTravelInquiryAdmin(ReadAwareAdmin):
    list_display = ("unread_badge", "organization_name", "contact_person", "email", "organization_type", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("organization_name", "contact_person", "email")


@admin.register(CorporateInquiry)
class CorporateInquiryAdmin(ReadAwareAdmin):
    list_display = ("unread_badge", "company_name", "full_name", "email", "service_needs", "is_resolved", "created_at")
    list_filter = ("is_read", "service_needs", "is_resolved", "created_at")
    search_fields = ("company_name", "full_name", "email", "service_needs")


@admin.register(PackageQuoteInquiry)
class PackageQuoteInquiryAdmin(ReadAwareAdmin):
    list_display = (
        "unread_badge",
        "package_title",
        "full_name",
        "email",
        "phone",
        "number_of_travelers",
        "travel_date",
        "is_resolved",
        "created_at",
    )
    list_filter = ("is_read", "is_resolved", "created_at", "travel_date")
    search_fields = ("package_title", "package_slug", "full_name", "email", "phone")


@admin.register(HotelInquiry)
class HotelInquiryAdmin(ReadAwareAdmin):
    list_display = (
        "unread_badge",
        "hotel_name",
        "full_name",
        "email",
        "phone",
        "check_in_date",
        "check_out_date",
        "number_of_guests",
        "is_resolved",
        "created_at",
    )
    list_filter = ("is_read", "is_resolved", "created_at", "check_in_date", "check_out_date", "airport_transfer_needed")
    search_fields = ("hotel_name", "hotel_slug", "full_name", "email", "phone")


@admin.register(CareerApplication)
class CareerApplicationAdmin(ReadAwareAdmin):
    list_display = (
        "unread_badge",
        "job",
        "full_name",
        "email",
        "primary_phone",
        "is_read",
        "status",
        "created_at",
    )
    list_filter = ("is_read", "status", "job", "created_at")
    search_fields = ("job__title", "full_name", "email", "primary_phone", "alt_phone")
    readonly_fields = (
        "cv_file_uuid",
        "cv_file_url",
        "cv_file_name",
        "cv_file_size",
        "cover_file_uuid",
        "cover_file_url",
        "cover_file_name",
        "cover_file_size",
        "created_at",
    )


@admin.register(TripFeedback)
class TripFeedbackAdmin(ReadAwareAdmin):
    list_display = (
        "unread_badge",
        "trip_name",
        "destination",
        "full_name",
        "email",
        "overall_rating",
        "likelihood_to_recommend",
        "created_at",
    )
    list_filter = ("is_read", "is_resolved", "created_at", "expectation_result", "would_travel_again")
    search_fields = ("trip_name", "destination", "full_name", "email", "interested_destinations")
