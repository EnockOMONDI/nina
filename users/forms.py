import re
import json
from urllib.parse import urlparse

from django import forms
from django.conf import settings
from django.utils import timezone

from adminside.models import CareerJob, Hotel, PackageHotelOption

from .models import CareerApplication, ContactInquiry, CorporateInquiry, HotelInquiry, PackageQuoteInquiry, TripFeedback


TRAVEL_CATEGORY_CHOICES = (
    ("Corporate Travel Management", "Corporate Travel Management"),
    ("Tours, Holidays & Safaris", "Tours, Holidays & Safaris"),
    ("Visa Facilitation", "Visa Facilitation"),
    ("Travel Insurance", "Travel Insurance"),
    ("Pre-Online Check-In", "Pre-Online Check-In"),
    ("Airport Transfers", "Airport Transfers"),
    ("Health Advisory Requirements", "Health Advisory Requirements"),
    ("Meetings & Conference Facilitation", "Meetings & Conference Facilitation"),
    ("Corporate Travel", "Corporate Travel"),
    ("Ticketing & Reservations", "Ticketing & Reservations"),
    ("General Inquiry", "General Inquiry"),
)

BUDGET_RANGE_CHOICES = (
    ("Under $1,000", "Under $1,000"),
    ("$1,000 - $2,500", "$1,000 - $2,500"),
    ("$2,500 - $5,000", "$2,500 - $5,000"),
    ("$5,000 - $10,000", "$5,000 - $10,000"),
    ("Above $10,000", "Above $10,000"),
    ("Not Sure Yet", "Not Sure Yet"),
)


class ContactForm(forms.ModelForm):
    subject = forms.ChoiceField(choices=TRAVEL_CATEGORY_CHOICES)

    class Meta:
        model = ContactInquiry
        fields = [
            "full_name",
            "email",
            "phone",
            "company",
            "subject",
            "message",
            "privacy_consent",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["full_name"].required = True
        self.fields["full_name"].widget.attrs.update(
            {
                "class": "w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-slate-900 focus:border-[#da176e] focus:ring-2 focus:ring-[#da176e]/15 outline-none",
                "placeholder": "Brian Otieno",
            }
        )

        self.fields["email"].required = True
        self.fields["email"].widget.attrs.update(
            {
                "class": "w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-slate-900 focus:border-[#da176e] focus:ring-2 focus:ring-[#da176e]/15 outline-none",
                "placeholder": "brian.otieno@gmail.com",
            }
        )

        self.fields["phone"].required = False
        self.fields["phone"].widget.attrs.update(
            {
                "class": "w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-slate-900 focus:border-[#da176e] focus:ring-2 focus:ring-[#da176e]/15 outline-none",
                "placeholder": "07XX XXX XXX (optional)",
            }
        )

        self.fields["company"].required = False
        self.fields["company"].widget.attrs.update(
            {
                "class": "w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-slate-900 focus:border-[#da176e] focus:ring-2 focus:ring-[#da176e]/15 outline-none",
                "placeholder": "Company name (optional)",
            }
        )

        self.fields["subject"].required = True
        self.fields["subject"].widget.attrs.update(
            {
                "class": "w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-slate-900 focus:border-[#da176e] focus:ring-2 focus:ring-[#da176e]/15 outline-none appearance-none",
            }
        )

        self.fields["message"].required = True
        self.fields["message"].widget.attrs.update(
            {
                "class": "w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-slate-900 focus:border-[#da176e] focus:ring-2 focus:ring-[#da176e]/15 outline-none",
                "placeholder": "Tell us what you need and your preferred travel dates.",
                "rows": 4,
            }
        )

        self.fields["privacy_consent"].required = False
        self.fields["privacy_consent"].widget = forms.HiddenInput()


class CorporateInquiryForm(forms.ModelForm):
    class Meta:
        model = CorporateInquiry
        fields = [
            "full_name",
            "email",
            "phone",
            "company_name",
            "role_title",
            "monthly_travelers",
            "service_needs",
            "message",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["full_name"].required = True
        self.fields["full_name"].widget.attrs.update(
            {
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none",
                "placeholder": "Your full name",
            }
        )

        self.fields["email"].required = True
        self.fields["email"].widget.attrs.update(
            {
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none",
                "placeholder": "Work email",
            }
        )

        self.fields["phone"].required = False
        self.fields["phone"].widget.attrs.update(
            {
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none",
                "placeholder": "+254 XXX XXX XXX",
            }
        )

        self.fields["company_name"].required = True
        self.fields["company_name"].widget.attrs.update(
            {
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none",
                "placeholder": "Company name",
            }
        )

        self.fields["role_title"].required = False
        self.fields["role_title"].widget.attrs.update(
            {
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none",
                "placeholder": "Your role/title",
            }
        )

        self.fields["monthly_travelers"].required = False
        self.fields["monthly_travelers"].widget.attrs.update(
            {
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none",
                "placeholder": "Estimated travelers per month",
                "min": "1",
            }
        )

        self.fields["service_needs"].required = True
        self.fields["service_needs"].widget.attrs.update(
            {
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none appearance-none",
            }
        )

        self.fields["message"].required = True
        self.fields["message"].widget.attrs.update(
            {
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none",
                "placeholder": "Share your corporate travel requirements, timelines, and priorities.",
                "rows": 5,
            }
        )


class PackageQuoteInquiryForm(forms.ModelForm):
    hotel_option = forms.ChoiceField(required=False)

    class Meta:
        model = PackageQuoteInquiry
        fields = [
            "package_title",
            "package_slug",
            "package_location",
            "package_duration",
            "package_price",
            "full_name",
            "email",
            "phone",
            "number_of_travelers",
            "travel_date",
            "budget_range",
            "special_requests",
        ]
        widgets = {
            "package_title": forms.HiddenInput(),
            "package_slug": forms.HiddenInput(),
            "package_location": forms.HiddenInput(),
            "package_duration": forms.HiddenInput(),
            "package_price": forms.HiddenInput(),
            "travel_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        package = kwargs.pop("package", None)
        super().__init__(*args, **kwargs)

        self.fields["full_name"].required = True
        self.fields["full_name"].widget.attrs.update(
            {
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none",
                "placeholder": "Brian Otieno",
            }
        )

        self.fields["email"].required = True
        self.fields["email"].widget.attrs.update(
            {
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none",
                "placeholder": "brian.otieno@gmail.com",
            }
        )

        self.fields["phone"].required = True
        self.fields["phone"].widget.attrs.update(
            {
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none",
                "placeholder": "07XX XXX XXX",
            }
        )

        self.fields["number_of_travelers"].required = True
        self.fields["number_of_travelers"].widget.attrs.update(
            {
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none",
                "placeholder": "4",
                "min": "1",
            }
        )

        self.fields["travel_date"].required = False
        self.fields["travel_date"].widget.attrs.update(
            {
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none",
            }
        )

        self.fields["budget_range"].required = False
        self.fields["budget_range"].widget = forms.Select(
            choices=(("", "Select budget range (optional)"),) + BUDGET_RANGE_CHOICES,
            attrs={
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none appearance-none",
            },
        )
        self.fields["special_requests"].required = False
        self.fields["special_requests"].widget.attrs.update(
            {
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none",
                "placeholder": "Share preferred dates, room setup, meal needs, or any custom requests.",
                "rows": 5,
            }
        )

        hotel_choices = [("", "Select hotel option (optional)")]
        if package:
            options = (
                PackageHotelOption.objects.filter(package=package, active=True)
                .select_related("hotel")
                .order_by("-is_recommended", "sort_order", "id")
            )
            option_count = 0
            for option in options:
                label_parts = [option.hotel.name]
                if option.room_type:
                    label_parts.append(option.room_type)
                if option.board_basis:
                    label_parts.append(option.board_basis)
                if option.nights:
                    label_parts.append(f"{option.nights} nights")
                if option.is_recommended:
                    label_parts.append("Recommended")
                hotel_choices.append((str(option.id), " | ".join(label_parts)))
                option_count += 1

            # Fallback: still provide options when package-specific mappings are not configured yet.
            if option_count == 0:
                fallback_hotels = Hotel.objects.filter(active=True).order_by("name")[:50]
                for hotel in fallback_hotels:
                    hotel_choices.append((f"hotel:{hotel.id}", f"{hotel.name} | General option"))

        self.fields["hotel_option"].choices = hotel_choices
        self.fields["hotel_option"].widget = forms.Select(
            attrs={
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-primary outline-none appearance-none",
            }
        )


class HotelInquiryForm(forms.ModelForm):
    class Meta:
        model = HotelInquiry
        fields = [
            "hotel_name",
            "hotel_slug",
            "hotel_location",
            "full_name",
            "email",
            "phone",
            "check_in_date",
            "check_out_date",
            "number_of_guests",
            "number_of_rooms",
            "room_preference",
            "meal_plan_preference",
            "budget_range",
            "airport_transfer_needed",
            "flexible_dates",
            "special_requests",
        ]
        widgets = {
            "hotel_name": forms.HiddenInput(),
            "hotel_slug": forms.HiddenInput(),
            "hotel_location": forms.HiddenInput(),
            "check_in_date": forms.DateInput(attrs={"type": "date"}),
            "check_out_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        hotel = kwargs.pop("hotel", None)
        super().__init__(*args, **kwargs)

        self.fields["budget_range"].required = False
        self.fields["budget_range"].widget = forms.Select(choices=[("", "Select budget range (optional)")] + list(BUDGET_RANGE_CHOICES))

        text_input_class = (
            "w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-slate-900 "
            "focus:border-[#da176e] focus:ring-2 focus:ring-[#da176e]/15 outline-none"
        )
        select_class = text_input_class + " appearance-none"

        self.fields["full_name"].widget.attrs.update({"class": text_input_class, "placeholder": "Enock Omondi"})
        self.fields["email"].widget.attrs.update({"class": text_input_class, "placeholder": "you@example.com"})
        self.fields["phone"].widget.attrs.update({"class": text_input_class, "placeholder": "+254 7XX XXX XXX"})
        self.fields["check_in_date"].widget.attrs.update({"class": text_input_class})
        self.fields["check_out_date"].widget.attrs.update({"class": text_input_class})
        self.fields["number_of_guests"].widget.attrs.update({"class": text_input_class, "min": 1})
        self.fields["number_of_rooms"].widget.attrs.update({"class": text_input_class, "min": 1})
        self.fields["room_preference"].widget.attrs.update({"class": select_class})
        self.fields["meal_plan_preference"].widget.attrs.update({"class": select_class})
        self.fields["budget_range"].widget.attrs.update({"class": select_class})
        self.fields["special_requests"].widget.attrs.update(
            {
                "class": text_input_class,
                "rows": 4,
                "placeholder": "Any room preference, transfer notes, celebrations, or special requests.",
            }
        )

        self.fields["airport_transfer_needed"].widget.attrs.update({"class": "h-4 w-4 rounded border-gray-300 text-[#da176e] focus:ring-[#da176e]"})
        self.fields["flexible_dates"].widget.attrs.update({"class": "h-4 w-4 rounded border-gray-300 text-[#da176e] focus:ring-[#da176e]"})

        if hotel:
            self.initial.setdefault("hotel_name", hotel.name)
            self.initial.setdefault("hotel_slug", hotel.slug)
            location = ", ".join([part for part in [hotel.city, hotel.region, hotel.country] if part]) or hotel.location
            self.initial.setdefault("hotel_location", location)

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get("check_in_date")
        check_out = cleaned.get("check_out_date")
        if check_in and check_out and check_out < check_in:
            self.add_error("check_out_date", "Check-out date cannot be earlier than check-in date.")
        return cleaned


class CareerApplicationForm(forms.ModelForm):
    job = forms.ModelChoiceField(
        queryset=CareerJob.objects.none(),
        empty_label="Select position",
    )
    cv_file_uuid = forms.CharField(widget=forms.HiddenInput())
    cv_file_url = forms.URLField(widget=forms.HiddenInput())
    cv_file_name = forms.CharField(required=False, widget=forms.HiddenInput())
    cv_file_size = forms.IntegerField(required=False, widget=forms.HiddenInput())

    cover_file_uuid = forms.CharField(required=False, widget=forms.HiddenInput())
    cover_file_url = forms.URLField(required=False, widget=forms.HiddenInput())
    cover_file_name = forms.CharField(required=False, widget=forms.HiddenInput())
    cover_file_size = forms.IntegerField(required=False, widget=forms.HiddenInput())

    honeypot = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = CareerApplication
        fields = [
            "job",
            "full_name",
            "email",
            "primary_phone",
            "alt_phone",
            "years_experience",
            "availability_date",
            "cover_letter_text",
            "cv_file_uuid",
            "cv_file_url",
            "cv_file_name",
            "cv_file_size",
            "cover_file_uuid",
            "cover_file_url",
            "cover_file_name",
            "cover_file_size",
            "honeypot",
        ]
        widgets = {
            "availability_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        selected_job = kwargs.pop("selected_job", None)
        super().__init__(*args, **kwargs)

        open_jobs = CareerJob.objects.filter(
            active=True,
            status=CareerJob.STATUS_OPEN,
        ).order_by("sort_order", "-created_at")
        self.fields["job"].queryset = open_jobs
        if selected_job:
            self.fields["job"].queryset = open_jobs.filter(id=selected_job.id)
            self.initial["job"] = selected_job

        text_input_class = "w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-slate-900 focus:border-[#da176e] focus:ring-2 focus:ring-[#da176e]/15 outline-none"
        select_input_class = "w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-slate-900 focus:border-[#da176e] focus:ring-2 focus:ring-[#da176e]/15 outline-none appearance-none"

        self.fields["job"].widget.attrs.update({"class": select_input_class})
        self.fields["full_name"].widget.attrs.update({"class": text_input_class, "placeholder": "Your full name"})
        self.fields["email"].widget.attrs.update({"class": text_input_class, "placeholder": "your@email.com"})
        self.fields["primary_phone"].widget.attrs.update({"class": text_input_class, "placeholder": "+254 7xx xxx xxx"})
        self.fields["alt_phone"].required = False
        self.fields["alt_phone"].widget.attrs.update({"class": text_input_class, "placeholder": "Alternative number (optional)"})
        self.fields["years_experience"].required = False
        self.fields["years_experience"].widget.attrs.update({"class": text_input_class, "placeholder": "e.g. 3", "min": "0"})
        self.fields["availability_date"].required = False
        self.fields["availability_date"].widget.attrs.update({"class": text_input_class})
        self.fields["cover_letter_text"].required = False
        self.fields["cover_letter_text"].widget = forms.Textarea(
            attrs={
                "class": text_input_class,
                "placeholder": "Optional: paste your cover letter text here.",
                "rows": 6,
            }
        )

    def _validate_uploadcare_file(self, file_uuid, file_url, file_name, file_size, label):
        if not file_uuid and not file_url:
            return

        uuid_pattern = re.compile(r"^[0-9a-fA-F-]{10,64}$")
        if not file_uuid or not uuid_pattern.match(file_uuid):
            raise forms.ValidationError(f"{label}: invalid file reference.")

        normalized_url = (file_url or "").strip()
        if normalized_url.startswith("//"):
            normalized_url = f"https:{normalized_url}"

        parsed = urlparse(normalized_url)
        host = parsed.netloc.lower()
        allowed_hosts = ("ucarecdn.com", "uploadcare.com", "ucarecd.net")
        host_allowed = any(host == domain or host.endswith(f".{domain}") for domain in allowed_hosts)
        if parsed.scheme not in {"https"} or not host_allowed:
            raise forms.ValidationError(f"{label}: invalid Uploadcare URL.")

        filename = (file_name or "").lower().strip()
        if filename:
            allowed_exts = getattr(settings, "CAREERS_ALLOWED_EXTENSIONS", ["pdf", "doc", "docx"])
            if "." not in filename or filename.rsplit(".", 1)[1] not in allowed_exts:
                raise forms.ValidationError(f"{label}: only PDF, DOC, and DOCX are allowed.")

        max_size = getattr(settings, "CAREERS_MAX_FILE_SIZE_BYTES", 10 * 1024 * 1024)
        if file_size and int(file_size) > max_size:
            raise forms.ValidationError(f"{label}: file exceeds 10MB limit.")

        return normalized_url

    def clean_honeypot(self):
        value = (self.cleaned_data.get("honeypot") or "").strip()
        if value:
            raise forms.ValidationError("Invalid submission.")
        return ""

    def clean_job(self):
        job = self.cleaned_data["job"]
        if not job.active or job.status != CareerJob.STATUS_OPEN:
            raise forms.ValidationError("This position is currently closed.")
        if job.deadline and job.deadline < timezone.localdate():
            raise forms.ValidationError("Application deadline for this position has passed.")
        return job

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["cv_file_url"] = self._validate_uploadcare_file(
            cleaned_data.get("cv_file_uuid"),
            cleaned_data.get("cv_file_url"),
            cleaned_data.get("cv_file_name"),
            cleaned_data.get("cv_file_size"),
            "CV",
        )

        cover_file_uuid = cleaned_data.get("cover_file_uuid")
        cover_file_url = cleaned_data.get("cover_file_url")
        cover_file_name = cleaned_data.get("cover_file_name")
        cover_file_size = cleaned_data.get("cover_file_size")
        cover_text = (cleaned_data.get("cover_letter_text") or "").strip()

        if cover_file_uuid or cover_file_url:
            cleaned_data["cover_file_url"] = self._validate_uploadcare_file(
                cover_file_uuid,
                cover_file_url,
                cover_file_name,
                cover_file_size,
                "Cover letter file",
            )

        if not cover_text and not cover_file_uuid:
            self.add_error(
                "cover_letter_text",
                "Add a cover letter text or upload a cover letter file.",
            )

        return cleaned_data


class TripFeedbackForm(forms.ModelForm):
    YES_NO_CHOICES = (
        ("", "Select"),
        ("yes", "Yes"),
        ("no", "No"),
    )

    EXPECTATION_CHOICES = (("", "Select"),) + TripFeedback.EXPECTATION_CHOICES
    TRAVEL_AGAIN_CHOICES = (("", "Select"),) + TripFeedback.TRAVEL_AGAIN_CHOICES

    CATEGORY_FIELDS = (
        ("transport", "Transport"),
        ("accommodation", "Accommodation"),
        ("tour_guide_driver", "Tour Guide / Driver"),
        ("communication", "Communication"),
        ("activities", "Activities"),
        ("value_for_money", "Value for Money"),
        ("logistics", "Logistics"),
        ("timeliness", "Timeliness"),
        ("professionalism", "Professionalism"),
        ("coordination", "Coordination"),
    )

    HIGHLIGHT_CHOICES = (
        ("Scenery", "Scenery"),
        ("Comfort", "Comfort"),
        ("Organization", "Organization"),
        ("Fun/Vibe", "Fun/Vibe"),
        ("Customer Service", "Customer Service"),
        ("Food", "Food"),
        ("Activities", "Activities"),
    )

    can_feature_publicly = forms.TypedChoiceField(
        choices=YES_NO_CHOICES,
        required=False,
        coerce=lambda val: True if val == "yes" else False if val == "no" else None,
    )
    can_use_media = forms.TypedChoiceField(
        choices=YES_NO_CHOICES,
        required=False,
        coerce=lambda val: True if val == "yes" else False if val == "no" else None,
    )
    highlights_selected = forms.MultipleChoiceField(
        choices=HIGHLIGHT_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    media_manifest = forms.CharField(required=False, widget=forms.HiddenInput())

    # Per-category optional ratings (1-10). Saved into category_ratings JSON.
    transport_rating = forms.IntegerField(required=False, min_value=1, max_value=10)
    accommodation_rating = forms.IntegerField(required=False, min_value=1, max_value=10)
    tour_guide_driver_rating = forms.IntegerField(required=False, min_value=1, max_value=10)
    communication_rating = forms.IntegerField(required=False, min_value=1, max_value=10)
    activities_rating = forms.IntegerField(required=False, min_value=1, max_value=10)
    value_for_money_rating = forms.IntegerField(required=False, min_value=1, max_value=10)
    logistics_rating = forms.IntegerField(required=False, min_value=1, max_value=10)
    timeliness_rating = forms.IntegerField(required=False, min_value=1, max_value=10)
    professionalism_rating = forms.IntegerField(required=False, min_value=1, max_value=10)
    coordination_rating = forms.IntegerField(required=False, min_value=1, max_value=10)

    class Meta:
        model = TripFeedback
        fields = [
            "trip_name",
            "destination",
            "travel_date",
            "full_name",
            "email",
            "phone",
            "can_feature_publicly",
            "overall_rating",
            "likelihood_to_recommend",
            "highlights_selected",
            "best_part",
            "improvements",
            "testimonial",
            "expectation_result",
            "would_travel_again",
            "interested_destinations",
            "can_use_media",
            "media_manifest",
        ]
        widgets = {
            "travel_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_class = (
            "w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-slate-900 "
            "focus:border-[#da176e] focus:ring-2 focus:ring-[#da176e]/15 outline-none"
        )
        select_class = input_class + " appearance-none"
        textarea_class = input_class

        self.fields["full_name"].required = True
        self.fields["email"].required = True

        self.fields["trip_name"].widget.attrs.update({"class": input_class, "placeholder": "e.g. 6 Days Mara Safari"})
        self.fields["destination"].widget.attrs.update({"class": input_class, "placeholder": "e.g. Maasai Mara"})
        self.fields["travel_date"].widget.attrs.update({"class": input_class})
        self.fields["full_name"].widget.attrs.update({"class": input_class, "placeholder": "Your full name"})
        self.fields["email"].widget.attrs.update({"class": input_class, "placeholder": "your@email.com"})
        self.fields["phone"].widget.attrs.update({"class": input_class, "placeholder": "+254 7XX XXX XXX (optional)"})
        self.fields["can_feature_publicly"].widget.attrs.update({"class": select_class})
        self.fields["overall_rating"].widget.attrs.update({"class": input_class, "min": "1", "max": "10", "placeholder": "1 - 10"})
        self.fields["likelihood_to_recommend"].widget.attrs.update({"class": input_class, "min": "0", "max": "10", "placeholder": "0 - 10"})
        self.fields["best_part"].widget = forms.Textarea(
            attrs={"class": textarea_class, "rows": 4, "placeholder": "What did you enjoy the most?"}
        )
        self.fields["improvements"].widget = forms.Textarea(
            attrs={"class": textarea_class, "rows": 4, "placeholder": "What can we improve?"}
        )
        self.fields["testimonial"].widget = forms.Textarea(
            attrs={"class": textarea_class, "rows": 4, "placeholder": "Write a short testimonial (optional)."}
        )
        self.fields["expectation_result"].widget.attrs.update({"class": select_class})
        self.fields["would_travel_again"].widget.attrs.update({"class": select_class})
        self.fields["interested_destinations"].widget = forms.Textarea(
            attrs={"class": textarea_class, "rows": 3, "placeholder": "e.g. Zanzibar, Amboseli, Dubai"}
        )
        self.fields["can_use_media"].widget.attrs.update({"class": select_class, "id": "id_can_use_media"})

        for key, _label in self.CATEGORY_FIELDS:
            field_name = f"{key}_rating"
            self.fields[field_name].widget.attrs.update(
                {
                    "class": input_class,
                    "min": "1",
                    "max": "10",
                    "placeholder": "1 - 10",
                }
            )

        self.category_field_rows = [
            (label, self[f"{key}_rating"])
            for key, label in self.CATEGORY_FIELDS
        ]

    def clean_media_manifest(self):
        raw = (self.cleaned_data.get("media_manifest") or "").strip()
        if not raw:
            return []

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid media upload payload.")

        if not isinstance(payload, list):
            raise forms.ValidationError("Invalid media upload payload.")

        cleaned_items = []
        for idx, item in enumerate(payload[:20]):
            if not isinstance(item, dict):
                continue

            uuid = str(item.get("uuid", "")).strip()
            cdn_url = str(item.get("cdnUrl", "")).strip()
            name = str(item.get("name", "")).strip()

            if not uuid or not cdn_url:
                continue

            if cdn_url.startswith("//"):
                cdn_url = f"https:{cdn_url}"

            parsed = urlparse(cdn_url)
            host = parsed.netloc.lower()
            allowed_hosts = ("ucarecdn.com", "uploadcare.com", "ucarecd.net")
            host_allowed = any(host == domain or host.endswith(f".{domain}") for domain in allowed_hosts)
            if parsed.scheme != "https" or not host_allowed:
                raise forms.ValidationError(f"Invalid media file URL at item {idx + 1}.")

            cleaned_items.append({"uuid": uuid, "cdnUrl": cdn_url, "name": name})

        return cleaned_items

    def clean(self):
        cleaned_data = super().clean()
        media_items = cleaned_data.get("media_manifest", [])
        cleaned_data["_media_items"] = media_items if isinstance(media_items, list) else []
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        category_ratings = {}
        for key, label in self.CATEGORY_FIELDS:
            value = self.cleaned_data.get(f"{key}_rating")
            if value not in (None, ""):
                category_ratings[label] = int(value)

        instance.category_ratings = category_ratings
        instance.highlights_selected = list(self.cleaned_data.get("highlights_selected") or [])

        media_items = self.cleaned_data.get("_media_items", [])
        instance.media_uuids = [item["uuid"] for item in media_items]
        instance.media_urls = [item["cdnUrl"] for item in media_items]
        instance.media_names = [item.get("name", "") for item in media_items]

        if commit:
            instance.save()
        return instance
