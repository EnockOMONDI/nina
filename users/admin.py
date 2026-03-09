from django.contrib import admin

from .models import (
    CareerApplication,
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


@admin.register(CareerApplication)
class CareerApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "job",
        "full_name",
        "email",
        "primary_phone",
        "status",
        "created_at",
    )
    list_filter = ("status", "job", "created_at")
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
