from django.conf import settings
from django.core.management.base import BaseCommand

from users.models import ContactInquiry
from users.tasks import send_contact_emails


class Command(BaseCommand):
    help = "Send a real test contact inquiry email via configured SMTP provider"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-email",
            default="ziadatoursandtravel@gmail.com",
            help="Recipient email for the user confirmation message",
        )
        parser.add_argument(
            "--admin-email",
            default=None,
            help="Override admin recipient email (defaults to settings.ADMIN_EMAIL)",
        )

    def handle(self, *args, **options):
        user_email = options["user_email"]
        admin_email = options["admin_email"] or settings.ADMIN_EMAIL

        self.stdout.write(self.style.NOTICE("Starting SMTP test email..."))
        self.stdout.write(self.style.NOTICE(f"EMAIL_PROVIDER={getattr(settings, 'EMAIL_PROVIDER', None)}"))
        self.stdout.write(self.style.NOTICE(f"EMAIL_HOST={getattr(settings, 'EMAIL_HOST', None)}"))
        self.stdout.write(self.style.NOTICE(f"EMAIL_PORT={getattr(settings, 'EMAIL_PORT', None)}"))
        self.stdout.write(self.style.NOTICE(f"EMAIL_HOST_USER={getattr(settings, 'EMAIL_HOST_USER', None)}"))
        self.stdout.write(self.style.NOTICE(f"DEFAULT_FROM_EMAIL={getattr(settings, 'DEFAULT_FROM_EMAIL', None)}"))
        self.stdout.write(self.style.NOTICE(f"ADMIN_EMAIL={admin_email}"))

        if getattr(settings, "EMAIL_HOST_PASSWORD", "").strip() in ("", "REPLACE_WITH_BREVO_SMTP_KEY"):
            self.stdout.write(self.style.ERROR("EMAIL_HOST_PASSWORD is missing or placeholder. Update your .env."))
            return

        inquiry = ContactInquiry.objects.create(
            full_name="Test Email",
            email=user_email,
            phone="",
            company="",
            subject="Test Inquiry",
            message="This is a real SMTP test from Ziada Tours.",
            privacy_consent=True,
        )

        original_admin = settings.ADMIN_EMAIL
        settings.ADMIN_EMAIL = admin_email
        try:
            self.stdout.write(self.style.NOTICE("Sending emails..."))
            send_contact_emails(inquiry)
        finally:
            settings.ADMIN_EMAIL = original_admin

        self.stdout.write(
            self.style.SUCCESS(
                f"Sent test emails to user={user_email} and admin={admin_email}."
            )
        )
