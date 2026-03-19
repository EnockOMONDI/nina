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
    is_read = models.BooleanField(default=False)
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
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Quote: {self.package_title} - {self.full_name}"


class HotelInquiry(models.Model):
    ROOM_PREFERENCE_CHOICES = (
        ("single", "Single"),
        ("double", "Double"),
        ("twin", "Twin"),
        ("family", "Family"),
        ("suite", "Suite"),
    )
    MEAL_PLAN_CHOICES = (
        ("room_only", "Room Only"),
        ("bb", "Bed & Breakfast (BB)"),
        ("hb", "Half Board (HB)"),
        ("fb", "Full Board (FB)"),
        ("ai", "All Inclusive (AI)"),
    )

    hotel = models.ForeignKey(
        "adminside.Hotel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inquiries",
    )

    hotel_name = models.CharField(max_length=220)
    hotel_slug = models.CharField(max_length=220, blank=True, default="")
    hotel_location = models.CharField(max_length=200, blank=True, default="")

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_guests = models.PositiveIntegerField(default=1)
    number_of_rooms = models.PositiveIntegerField(default=1)
    room_preference = models.CharField(max_length=20, choices=ROOM_PREFERENCE_CHOICES, blank=True, default="")
    meal_plan_preference = models.CharField(max_length=20, choices=MEAL_PLAN_CHOICES, blank=True, default="")
    budget_range = models.CharField(max_length=120, blank=True, default="")
    airport_transfer_needed = models.BooleanField(default=False)
    flexible_dates = models.BooleanField(default=False)
    special_requests = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Hotel Inquiry: {self.hotel_name} - {self.full_name}"


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
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company_name} - {self.full_name}"


class CareerApplication(models.Model):
    STATUS_NEW = "new"
    STATUS_REVIEWING = "reviewing"
    STATUS_SHORTLISTED = "shortlisted"
    STATUS_REJECTED = "rejected"
    STATUS_HIRED = "hired"
    STATUS_CHOICES = (
        (STATUS_NEW, "New"),
        (STATUS_REVIEWING, "Reviewing"),
        (STATUS_SHORTLISTED, "Shortlisted"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_HIRED, "Hired"),
    )

    job = models.ForeignKey(
        "adminside.CareerJob",
        on_delete=models.PROTECT,
        related_name="applications",
    )
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    primary_phone = models.CharField(max_length=20)
    alt_phone = models.CharField(max_length=20, blank=True, default="")
    years_experience = models.PositiveIntegerField(blank=True, null=True)
    availability_date = models.DateField(blank=True, null=True)
    cover_letter_text = models.TextField(blank=True, default="")

    cv_file_uuid = models.CharField(max_length=64)
    cv_file_url = models.URLField(max_length=500)
    cv_file_name = models.CharField(max_length=255, blank=True, default="")
    cv_file_size = models.PositiveIntegerField(blank=True, null=True)

    cover_file_uuid = models.CharField(max_length=64, blank=True, default="")
    cover_file_url = models.URLField(max_length=500, blank=True, default="")
    cover_file_name = models.CharField(max_length=255, blank=True, default="")
    cover_file_size = models.PositiveIntegerField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.job.title}"


DEFAULT_FEEDBACK_CATEGORIES = [
    "Transport",
    "Accommodation",
    "Tour Guide / Driver",
    "Communication",
    "Activities",
    "Value for Money",
    "Logistics",
    "Timeliness",
    "Professionalism",
    "Coordination",
]

DEFAULT_FEEDBACK_HIGHLIGHTS = [
    "Scenery",
    "Comfort",
    "Organization",
    "Fun/Vibe",
    "Customer Service",
    "Food",
    "Activities",
]


class TripFeedback(models.Model):
    EXPECTATION_CHOICES = (
        ("exceeded", "Exceeded"),
        ("met", "Met"),
        ("below", "Below"),
    )
    TRAVEL_AGAIN_CHOICES = (
        ("yes", "Yes"),
        ("maybe", "Maybe"),
        ("no", "No"),
    )

    trip_name = models.CharField(max_length=220, blank=True, default="")
    destination = models.CharField(max_length=220, blank=True, default="")
    travel_date = models.DateField(null=True, blank=True)

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, default="")
    can_feature_publicly = models.BooleanField(null=True, blank=True)

    overall_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    likelihood_to_recommend = models.PositiveSmallIntegerField(null=True, blank=True)

    category_ratings = models.JSONField(default=dict, blank=True)
    highlights_selected = models.JSONField(default=list, blank=True)

    best_part = models.TextField(blank=True, default="")
    improvements = models.TextField(blank=True, default="")
    testimonial = models.TextField(blank=True, default="")

    expectation_result = models.CharField(max_length=20, choices=EXPECTATION_CHOICES, blank=True, default="")
    would_travel_again = models.CharField(max_length=10, choices=TRAVEL_AGAIN_CHOICES, blank=True, default="")
    interested_destinations = models.TextField(blank=True, default="")

    can_use_media = models.BooleanField(null=True, blank=True)
    media_urls = models.JSONField(default=list, blank=True)
    media_uuids = models.JSONField(default=list, blank=True)
    media_names = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        trip = self.trip_name or self.destination or "Trip Feedback"
        return f"{trip} - {self.full_name}"


class MICEInquiry(models.Model):
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    event_type = models.CharField(max_length=100)
    attendees = models.PositiveIntegerField()
    event_details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

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
    is_read = models.BooleanField(default=False)

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
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.organization_name
