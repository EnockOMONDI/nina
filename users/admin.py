from django.contrib import admin

from .models import (
    ContactInquiry,
    CorporateInquiry,
    MICEInquiry,
    StudentTravelInquiry,
    NGOTravelInquiry,
    PackageQuoteInquiry,
)


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "subject", "is_resolved", "created_at")
    list_filter = ("is_resolved", "created_at")
    search_fields = ("full_name", "email", "subject")


@admin.register(MICEInquiry)
class MICEInquiryAdmin(admin.ModelAdmin):
    list_display = ("company_name", "contact_person", "email", "event_type", "created_at")
    search_fields = ("company_name", "contact_person", "email")


@admin.register(StudentTravelInquiry)
class StudentTravelInquiryAdmin(admin.ModelAdmin):
    list_display = ("school_name", "contact_person", "email", "program_stage", "created_at")
    search_fields = ("school_name", "contact_person", "email")


@admin.register(NGOTravelInquiry)
class NGOTravelInquiryAdmin(admin.ModelAdmin):
    list_display = ("organization_name", "contact_person", "email", "organization_type", "created_at")
    search_fields = ("organization_name", "contact_person", "email")


@admin.register(CorporateInquiry)
class CorporateInquiryAdmin(admin.ModelAdmin):
    list_display = ("company_name", "full_name", "email", "service_needs", "is_resolved", "created_at")
    list_filter = ("service_needs", "is_resolved", "created_at")
    search_fields = ("company_name", "full_name", "email", "service_needs")


@admin.register(PackageQuoteInquiry)
class PackageQuoteInquiryAdmin(admin.ModelAdmin):
    list_display = (
        "package_title",
        "full_name",
        "email",
        "phone",
        "number_of_travelers",
        "travel_date",
        "is_resolved",
        "created_at",
    )
    list_filter = ("is_resolved", "created_at", "travel_date")
    search_fields = ("package_title", "package_slug", "full_name", "email", "phone")
