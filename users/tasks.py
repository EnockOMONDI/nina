from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
import requests

try:
    from mailtrap import Mail, Address, MailtrapClient
except Exception:
    Mail = None
    Address = None
    MailtrapClient = None


def send_email_via_mailtrap(subject, html_message, from_email, recipient_list):
    if MailtrapClient is None:
        raise RuntimeError("Mailtrap client is not available. Install mailtrap package.")

    client = MailtrapClient(token=settings.MAILTRAP_API_TOKEN)

    if "<" in from_email and ">" in from_email:
        from_name = from_email.split("<")[0].strip()
        from_email_addr = from_email.split("<")[1].split(">")[0].strip()
    else:
        from_name = "Nina Tours & Travel Ltd"
        from_email_addr = from_email.strip()

    mail = Mail(
        sender=Address(email=from_email_addr, name=from_name),
        to=[Address(email=email.strip()) for email in recipient_list],
        subject=subject,
        html=html_message,
    )

    client.send(mail)
    return True


def send_email(subject, html_message, recipient_list):
    provider = str(getattr(settings, "EMAIL_PROVIDER", "smtp")).strip().lower()
    from_email = settings.DEFAULT_FROM_EMAIL

    if provider == "mailtrap_api":
        return send_email_via_mailtrap(subject, html_message, from_email, recipient_list)
    if provider in {"brevo_api", "brevo"}:
        return send_email_via_brevo_api(subject, html_message, from_email, recipient_list)

    email = EmailMessage(subject, html_message, from_email, recipient_list)
    email.content_subtype = "html"
    email.send(fail_silently=False)
    return True


def _admin_change_url(route_name, obj_id):
    base = getattr(settings, "SITE_URL", "").rstrip("/")
    path = reverse(route_name, args=[obj_id])
    return f"{base}{path}" if base else path


def send_email_via_brevo_api(subject, html_message, from_email, recipient_list):
    api_key = getattr(settings, "BREVO_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Brevo API key is missing. Set BREVO_API_KEY.")

    recipients = [{"email": email.strip()} for email in recipient_list if email and email.strip()]
    if not recipients:
        raise RuntimeError("Recipient list is empty.")

    sender_email = getattr(settings, "BREVO_SENDER_EMAIL", "").strip()
    sender_name = getattr(settings, "BREVO_SENDER_NAME", "").strip()
    if not sender_email:
        if "<" in from_email and ">" in from_email:
            sender_email = from_email.split("<")[1].split(">")[0].strip()
        else:
            sender_email = from_email.strip()
    if not sender_name:
        if "<" in from_email and ">" in from_email:
            sender_name = from_email.split("<")[0].strip()
        else:
            sender_name = "Nina Tours & Travel Ltd"

    payload = {
        "sender": {"email": sender_email, "name": sender_name},
        "to": recipients,
        "subject": subject,
        "htmlContent": html_message,
    }

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        },
        json=payload,
        timeout=getattr(settings, "EMAIL_TIMEOUT", 10),
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Brevo API send failed ({response.status_code}): {response.text[:300]}")
    return True


def send_contact_emails(inquiry):
    user_subject = "Nina Tours: We received your request"
    admin_subject = "NEW CONTACT INQUIRY"

    extra_recipients = [
        email.strip()
        for email in getattr(settings, "EXTRA_EMAIL_RECIPIENTS", [])
        if email.strip()
    ]

    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    user_html = render_to_string(
        "users/emails/user_confirmation.html",
        {
            "inquiry": inquiry,
            "site_url": site_url,
        },
    )
    admin_html = render_to_string(
        "users/emails/admin_notification.html",
        {
            "inquiry": inquiry,
            "site_url": site_url,
            "admin_change_url": _admin_change_url("admin:users_contactinquiry_change", inquiry.id),
        },
    )

    send_email(user_subject, user_html, [inquiry.email] + extra_recipients)
    send_email(admin_subject, admin_html, [settings.ADMIN_EMAIL] + extra_recipients)


def send_corporate_emails(inquiry):
    user_subject = "Nina Tours: We received your corporate travel inquiry"
    admin_subject = "NEW CORPORATE INQUIRY"

    extra_recipients = [
        email.strip()
        for email in getattr(settings, "EXTRA_EMAIL_RECIPIENTS", [])
        if email.strip()
    ]

    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    user_html = render_to_string(
        "users/emails/corporate_user_confirmation.html",
        {
            "inquiry": inquiry,
            "site_url": site_url,
        },
    )
    admin_html = render_to_string(
        "users/emails/corporate_admin_notification.html",
        {
            "inquiry": inquiry,
            "site_url": site_url,
            "admin_change_url": _admin_change_url("admin:users_corporateinquiry_change", inquiry.id),
        },
    )

    send_email(user_subject, user_html, [inquiry.email] + extra_recipients)
    send_email(admin_subject, admin_html, [settings.ADMIN_EMAIL] + extra_recipients)


def send_package_quote_emails(inquiry):
    user_subject = f"Nina Tours: We received your quote request for {inquiry.package_title}"
    admin_subject = f"NEW PACKAGE QUOTE INQUIRY - {inquiry.package_title}"

    extra_recipients = [
        email.strip()
        for email in getattr(settings, "EXTRA_EMAIL_RECIPIENTS", [])
        if email.strip()
    ]

    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    user_html = render_to_string(
        "users/emails/package_quote_user_confirmation.html",
        {
            "inquiry": inquiry,
            "site_url": site_url,
        },
    )
    admin_html = render_to_string(
        "users/emails/package_quote_admin_notification.html",
        {
            "inquiry": inquiry,
            "site_url": site_url,
            "admin_change_url": _admin_change_url("admin:users_packagequoteinquiry_change", inquiry.id),
        },
    )

    send_email(user_subject, user_html, [inquiry.email] + extra_recipients)
    send_email(admin_subject, admin_html, [settings.ADMIN_EMAIL] + extra_recipients)


def send_hotel_inquiry_emails(inquiry):
    user_subject = f"Nina Tours: We received your hotel inquiry for {inquiry.hotel_name}"
    admin_subject = f"NEW HOTEL INQUIRY - {inquiry.hotel_name}"

    extra_recipients = [
        email.strip()
        for email in getattr(settings, "EXTRA_EMAIL_RECIPIENTS", [])
        if email.strip()
    ]

    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    user_html = render_to_string(
        "users/emails/hotel_inquiry_user_confirmation.html",
        {
            "inquiry": inquiry,
            "site_url": site_url,
        },
    )
    admin_html = render_to_string(
        "users/emails/hotel_inquiry_admin_notification.html",
        {
            "inquiry": inquiry,
            "site_url": site_url,
            "admin_change_url": _admin_change_url("admin:users_hotelinquiry_change", inquiry.id),
        },
    )

    send_email(user_subject, user_html, [inquiry.email] + extra_recipients)
    send_email(admin_subject, admin_html, [settings.ADMIN_EMAIL] + extra_recipients)


def send_career_application_emails(application):
    user_subject = f"Nina Tours: We received your application for {application.job.title}"
    admin_subject = f"NEW CAREER APPLICATION - {application.job.title}"

    extra_recipients = [
        email.strip()
        for email in getattr(settings, "EXTRA_EMAIL_RECIPIENTS", [])
        if email.strip()
    ]

    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    user_html = render_to_string(
        "users/emails/career_application_user_confirmation.html",
        {
            "application": application,
            "site_url": site_url,
        },
    )
    admin_html = render_to_string(
        "users/emails/career_application_admin_notification.html",
        {
            "application": application,
            "site_url": site_url,
            "admin_change_url": _admin_change_url("admin:users_careerapplication_change", application.id),
        },
    )

    send_email(user_subject, user_html, [application.email] + extra_recipients)
    send_email(
        admin_subject,
        admin_html,
        [getattr(settings, "JOBS_EMAIL", settings.ADMIN_EMAIL)] + extra_recipients,
    )


def send_trip_feedback_emails(feedback):
    user_subject = "Nina Tours: Thank you for sharing your trip feedback"
    admin_subject = "NEW TRIP FEEDBACK"

    extra_recipients = [
        email.strip()
        for email in getattr(settings, "EXTRA_EMAIL_RECIPIENTS", [])
        if email.strip()
    ]

    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    user_html = render_to_string(
        "users/emails/trip_feedback_user_confirmation.html",
        {
            "feedback": feedback,
            "site_url": site_url,
        },
    )
    admin_html = render_to_string(
        "users/emails/trip_feedback_admin_notification.html",
        {
            "feedback": feedback,
            "site_url": site_url,
            "admin_change_url": _admin_change_url("admin:users_tripfeedback_change", feedback.id),
        },
    )

    send_email(user_subject, user_html, [feedback.email] + extra_recipients)
    send_email(admin_subject, admin_html, [settings.ADMIN_EMAIL] + extra_recipients)
