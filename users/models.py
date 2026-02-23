from django.db import models


class ContactInquiry(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    privacy_consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.subject}"


class PackageQuoteInquiry(models.Model):
    package = models.ForeignKey(
        "adminside.Package",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quote_inquiries",
    )

    package_title = models.CharField(max_length=200)
    package_slug = models.CharField(max_length=220, blank=True, default="")
    package_location = models.CharField(max_length=150, blank=True, default="")
    package_duration = models.CharField(max_length=100, blank=True, default="")
    package_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    number_of_travelers = models.PositiveIntegerField(default=1)
    travel_date = models.DateField(null=True, blank=True)
    budget_range = models.CharField(max_length=120, blank=True, default="")
    special_requests = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Quote: {self.package_title} - {self.full_name}"


class CorporateInquiry(models.Model):
    SERVICE_NEEDS_CHOICES = (
        ("Managed Corporate Travel", "Managed Corporate Travel"),
        ("Executive & VIP Travel", "Executive & VIP Travel"),
        ("Conference & Event Travel", "Conference & Event Travel"),
        ("Group & Project Travel", "Group & Project Travel"),
        ("Travel Policy & Cost Optimization", "Travel Policy & Cost Optimization"),
        ("Other", "Other"),
    )

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=200)
    role_title = models.CharField(max_length=120, blank=True)
    monthly_travelers = models.PositiveIntegerField(blank=True, null=True)
    service_needs = models.CharField(max_length=120, choices=SERVICE_NEEDS_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company_name} - {self.full_name}"


class MICEInquiry(models.Model):
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    event_type = models.CharField(max_length=100)
    attendees = models.PositiveIntegerField()
    event_details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.company_name


class StudentTravelInquiry(models.Model):
    school_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    program_stage = models.CharField(max_length=100)
    number_of_students = models.PositiveIntegerField()
    travel_details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.school_name


class NGOTravelInquiry(models.Model):
    organization_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    organization_type = models.CharField(max_length=100)
    travel_purpose = models.TextField()
    number_of_travelers = models.PositiveIntegerField()
    travel_details = models.TextField()
    sustainability_requirements = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.organization_name
