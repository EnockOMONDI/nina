from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from adminside.models import Package

from .models import ContactInquiry, CorporateInquiry, PackageQuoteInquiry


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    EMAIL_PROVIDER="smtp",
    DEFAULT_FROM_EMAIL="Ziada Tours and Travel <info@ziadatoursandtravel.com>",
    ADMIN_EMAIL="info@ziadatoursandtravel.com",
)
class ContactInquiryEmailTests(TestCase):
    def test_contact_inquiry_saves_and_sends_emails(self):
        payload = {
            "full_name": "Test User",
            "email": "user@example.com",
            "phone": "0700000000",
            "company": "Test Co",
            "subject": "Safari Experience",
            "message": "I want to plan a safari.",
            "privacy_consent": "on",
        }

        response = self.client.post(reverse("contact"), data=payload, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactInquiry.objects.count(), 1)

        inquiry = ContactInquiry.objects.first()
        self.assertEqual(inquiry.email, payload["email"])
        self.assertEqual(inquiry.subject, payload["subject"])

        self.assertEqual(len(mail.outbox), 2)
        subjects = {email.subject for email in mail.outbox}
        self.assertIn("We received your request", subjects)
        self.assertIn("New contact inquiry", subjects)

        to_addresses = {email.to[0] for email in mail.outbox}
        self.assertIn("user@example.com", to_addresses)
        self.assertIn("info@ziadatoursandtravel.com", to_addresses)

        for email in mail.outbox:
            self.assertEqual(email.from_email, "Ziada Tours and Travel <info@ziadatoursandtravel.com>")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    EMAIL_PROVIDER="smtp",
    DEFAULT_FROM_EMAIL="Ziada Tours and Travel <info@ziadatoursandtravel.com>",
    ADMIN_EMAIL="info@ziadatoursandtravel.com",
)
class CorporateInquiryEmailTests(TestCase):
    def test_corporate_inquiry_saves_and_sends_emails(self):
        payload = {
            "full_name": "Corporate User",
            "email": "corp@example.com",
            "phone": "0700000000",
            "company_name": "Acme Corp",
            "role_title": "Travel Manager",
            "monthly_travelers": 24,
            "service_needs": "Managed Corporate Travel",
            "message": "We need monthly regional travel support.",
        }

        response = self.client.post(reverse("corporates"), data=payload, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CorporateInquiry.objects.count(), 1)

        inquiry = CorporateInquiry.objects.first()
        self.assertEqual(inquiry.email, payload["email"])
        self.assertEqual(inquiry.company_name, payload["company_name"])

        self.assertEqual(len(mail.outbox), 2)
        subjects = {email.subject for email in mail.outbox}
        self.assertIn("We received your corporate travel inquiry", subjects)
        self.assertIn("New corporate inquiry", subjects)

        to_addresses = {email.to[0] for email in mail.outbox}
        self.assertIn("corp@example.com", to_addresses)
        self.assertIn("info@ziadatoursandtravel.com", to_addresses)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    EMAIL_PROVIDER="smtp",
    DEFAULT_FROM_EMAIL="Ziada Tours and Travel <info@ziadatoursandtravel.com>",
    ADMIN_EMAIL="info@ziadatoursandtravel.com",
)
class PackageQuoteInquiryEmailTests(TestCase):
    def test_package_quote_saves_and_sends_emails(self):
        package = Package.objects.create(
            title="Maasai Mara Safari",
            slug="maasai-mara-safari",
            duration="5 days / 4 nights",
            price=1299,
            location="Maasai Mara",
            category="Safari",
            active=True,
        )

        payload = {
            "package_title": package.title,
            "package_slug": package.slug,
            "package_location": package.location,
            "package_duration": package.duration,
            "package_price": package.price,
            "full_name": "Quote User",
            "email": "quote@example.com",
            "phone": "0700000000",
            "number_of_travelers": 4,
            "travel_date": "2026-08-01",
            "budget_range": "$2,500 - $5,000",
            "special_requests": "Family-friendly itinerary and private transfer.",
        }

        response = self.client.post(reverse("package-quote"), data=payload, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(PackageQuoteInquiry.objects.count(), 1)

        inquiry = PackageQuoteInquiry.objects.first()
        self.assertEqual(inquiry.email, payload["email"])
        self.assertEqual(inquiry.package_title, package.title)
        self.assertEqual(inquiry.package, package)
        self.assertEqual(inquiry.number_of_travelers, payload["number_of_travelers"])

        self.assertEqual(len(mail.outbox), 2)
        subjects = {email.subject for email in mail.outbox}
        self.assertIn(f"We received your quote request for {package.title}", subjects)
        self.assertIn(f"New package quote inquiry - {package.title}", subjects)
