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
            "subject": "Tours, Holidays & Safaris",
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
        self.assertIn("Nina Tours: We received your request", subjects)
        self.assertIn("NEW CONTACT INQUIRY", subjects)

        to_addresses = {email.to[0] for email in mail.outbox}
        self.assertIn("user@example.com", to_addresses)
        self.assertIn("info@ziadatoursandtravel.com", to_addresses)

        for email in mail.outbox:
            self.assertEqual(email.from_email, "Ziada Tours and Travel <info@ziadatoursandtravel.com>")

    @override_settings(
        PUBLIC_FORM_BLOCKED_NAMES=["robertmus"],
        PUBLIC_FORM_BLOCKED_EMAILS=[],
        PUBLIC_FORM_BLOCKED_IPS=[],
    )
    def test_blocked_contact_name_is_not_saved_or_emailed(self):
        payload = {
            "full_name": "RobertMus",
            "email": "blocked@example.com",
            "phone": "0700000000",
            "company": "Spam Co",
            "subject": "Tours, Holidays & Safaris",
            "message": "Spam submission.",
            "privacy_consent": "on",
        }

        response = self.client.post(reverse("contact"), data=payload, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactInquiry.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)
        self.assertContains(response, "This sender has been blocked for spam")

    @override_settings(
        PUBLIC_FORM_BLOCKED_NAMES=[],
        PUBLIC_FORM_BLOCKED_EMAILS=["blocked@example.com"],
        PUBLIC_FORM_BLOCKED_IPS=[],
    )
    def test_blocked_contact_email_is_not_saved_or_emailed(self):
        payload = {
            "full_name": "Blocked User",
            "email": "blocked@example.com",
            "phone": "0700000000",
            "company": "Spam Co",
            "subject": "Tours, Holidays & Safaris",
            "message": "Spam submission.",
            "privacy_consent": "on",
        }

        response = self.client.post(reverse("contact"), data=payload, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactInquiry.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)
        self.assertContains(response, "This sender has been blocked for spam")

    @override_settings(
        PUBLIC_FORM_BLOCKED_NAMES=[],
        PUBLIC_FORM_BLOCKED_EMAILS=[],
        PUBLIC_FORM_BLOCKED_IPS=["203.0.113.10"],
    )
    def test_blocked_contact_forwarded_ip_is_not_saved_or_emailed(self):
        payload = {
            "full_name": "Blocked User",
            "email": "user@example.com",
            "phone": "0700000000",
            "company": "Spam Co",
            "subject": "Tours, Holidays & Safaris",
            "message": "Spam submission.",
            "privacy_consent": "on",
        }

        response = self.client.post(
            reverse("contact"),
            data=payload,
            HTTP_X_FORWARDED_FOR="203.0.113.10, 10.0.0.1",
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactInquiry.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)
        self.assertContains(response, "This sender has been blocked for spam")


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
        self.assertIn("Nina Tours: We received your corporate travel inquiry", subjects)
        self.assertIn("NEW CORPORATE INQUIRY", subjects)

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
        self.assertIn(f"Nina Tours: We received your quote request for {package.title}", subjects)
        self.assertIn(f"NEW PACKAGE QUOTE INQUIRY - {package.title}", subjects)
