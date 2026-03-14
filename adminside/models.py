from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


class Destination(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Package(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    duration = models.CharField(max_length=100, blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    destination = models.ForeignKey(
        Destination,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="packages",
    )
    location = models.CharField(max_length=150, blank=True, default="")
    category = models.CharField(max_length=100, blank=True, default="")
    image_url = models.URLField(blank=True, default="")
    description = CKEditor5Field(config_name="default", blank=True, default="")
    pricing_table_html = CKEditor5Field(config_name="default", blank=True, default="")
    inclusions = models.TextField(blank=True, default="")
    exclusions = models.TextField(blank=True, default="")
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    min_group_size = models.PositiveIntegerField(blank=True, null=True)
    max_group_size = models.PositiveIntegerField(blank=True, null=True)
    starting_price_note = models.CharField(max_length=160, blank=True, default="")
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


class PackageMarketPrice(models.Model):
    MARKET_LOCAL = "local"
    MARKET_INTERNATIONAL = "international"
    MARKET_CHOICES = [
        (MARKET_LOCAL, "Local"),
        (MARKET_INTERNATIONAL, "International"),
    ]

    CURRENCY_KES = "KES"
    CURRENCY_USD = "USD"
    CURRENCY_CHOICES = [
        (CURRENCY_KES, "KES"),
        (CURRENCY_USD, "USD"),
    ]

    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="market_prices",
    )
    market = models.CharField(max_length=20, choices=MARKET_CHOICES)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.CharField(max_length=200, blank=True, default="")
    active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["package", "market"],
                name="uniq_package_market_price_market",
            )
        ]

    def __str__(self):
        return f"{self.package.title} - {self.get_market_display()} ({self.currency} {self.amount})"


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
    city = models.CharField(max_length=120, blank=True, default="")
    region = models.CharField(max_length=120, blank=True, default="")
    country = models.CharField(max_length=120, blank=True, default="Kenya")
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


class CareerJob(models.Model):
    JOB_TYPE_FULL_TIME = "full_time"
    JOB_TYPE_PART_TIME = "part_time"
    JOB_TYPE_CONTRACT = "contract"
    JOB_TYPE_INTERNSHIP = "internship"
    JOB_TYPE_CHOICES = [
        (JOB_TYPE_FULL_TIME, "Full-time"),
        (JOB_TYPE_PART_TIME, "Part-time"),
        (JOB_TYPE_CONTRACT, "Contract"),
        (JOB_TYPE_INTERNSHIP, "Internship"),
    ]

    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_CLOSED, "Closed"),
    ]

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True)
    department = models.CharField(max_length=120, blank=True, default="")
    location = models.CharField(max_length=150, blank=True, default="")
    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        default=JOB_TYPE_FULL_TIME,
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    hero_image_url = models.URLField(blank=True, default="")
    summary = models.TextField(blank=True, default="")
    description = CKEditor5Field(config_name="default", blank=True, default="")
    responsibilities = CKEditor5Field(config_name="default", blank=True, default="")
    requirements = CKEditor5Field(config_name="default", blank=True, default="")
    posted_on = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:240]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PackageAvailabilityMonth(models.Model):
    STATUS_AVAILABLE = "available"
    STATUS_LIMITED = "limited"
    STATUS_SOLD_OUT = "sold_out"
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
        (STATUS_LIMITED, "Limited"),
        (STATUS_SOLD_OUT, "Sold Out"),
    ]

    MONTH_CHOICES = [
        (1, "Jan"),
        (2, "Feb"),
        (3, "Mar"),
        (4, "Apr"),
        (5, "May"),
        (6, "Jun"),
        (7, "Jul"),
        (8, "Aug"),
        (9, "Sep"),
        (10, "Oct"),
        (11, "Nov"),
        (12, "Dec"),
    ]

    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="availability_months",
    )
    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE,
    )
    notes = models.CharField(max_length=255, blank=True, default="")
    active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["year", "month", "sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["package", "month", "year"],
                name="uniq_package_month_year",
            )
        ]

    def __str__(self):
        year_label = f" {self.year}" if self.year else ""
        return f"{self.package.title} - {self.get_month_display()}{year_label}"


class PackageHotelOption(models.Model):
    BOARD_BASIS_BB = "BB"
    BOARD_BASIS_HB = "HB"
    BOARD_BASIS_FB = "FB"
    BOARD_BASIS_AI = "AI"
    BOARD_BASIS_CHOICES = [
        (BOARD_BASIS_BB, "BB"),
        (BOARD_BASIS_HB, "HB"),
        (BOARD_BASIS_FB, "FB"),
        (BOARD_BASIS_AI, "AI"),
    ]

    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="hotel_options",
    )
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="package_options",
    )
    room_type = models.CharField(max_length=100, blank=True, default="")
    board_basis = models.CharField(
        max_length=2,
        choices=BOARD_BASIS_CHOICES,
        blank=True,
        default="",
    )
    nights = models.PositiveSmallIntegerField(blank=True, null=True)
    price_adjustment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    pricing_table_html = CKEditor5Field(config_name="default", blank=True, default="")
    is_recommended = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-is_recommended", "sort_order", "id"]

    def __str__(self):
        return f"{self.package.title} - {self.hotel.name}"
