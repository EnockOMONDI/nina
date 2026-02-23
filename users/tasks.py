from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
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
        from_name = "Ziada Travel"
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
            sender_name = "Ziada Tours and Travel"

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
    user_subject = "We received your request"
    admin_subject = "New contact inquiry"

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
        },
    )

    send_email(user_subject, user_html, [inquiry.email] + extra_recipients)
    send_email(admin_subject, admin_html, [settings.ADMIN_EMAIL] + extra_recipients)


def send_corporate_emails(inquiry):
    user_subject = "We received your corporate travel inquiry"
    admin_subject = "New corporate inquiry"

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
        },
    )

    send_email(user_subject, user_html, [inquiry.email] + extra_recipients)
    send_email(admin_subject, admin_html, [settings.ADMIN_EMAIL] + extra_recipients)


def send_package_quote_emails(inquiry):
    user_subject = f"We received your quote request for {inquiry.package_title}"
    admin_subject = f"New package quote inquiry - {inquiry.package_title}"

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
        },
    )

    send_email(user_subject, user_html, [inquiry.email] + extra_recipients)
    send_email(admin_subject, admin_html, [settings.ADMIN_EMAIL] + extra_recipients)
