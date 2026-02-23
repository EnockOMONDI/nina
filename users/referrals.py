from django.utils import timezone

from .models import ReferralClick, ReferralConsultant

REFERRAL_CODE_SESSION_KEY = "referral_code"
REFERRAL_CLICK_ID_SESSION_KEY = "referral_click_id"


def _get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def track_referral_from_request(request):
    referral_code = request.GET.get("ref", "").strip()
    if not referral_code:
        return None

    consultant = ReferralConsultant.objects.filter(code__iexact=referral_code, is_active=True).first()
    if not consultant:
        return None

    if not request.session.session_key:
        request.session.save()

    click = ReferralClick.objects.create(
        consultant=consultant,
        referral_code=consultant.code,
        landing_path=request.path,
        query_string=request.META.get("QUERY_STRING", ""),
        ip_address=_get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
        session_key=request.session.session_key or "",
    )

    request.session[REFERRAL_CODE_SESSION_KEY] = consultant.code
    request.session[REFERRAL_CLICK_ID_SESSION_KEY] = click.id
    return click


def apply_referral_to_inquiry(request, inquiry):
    referral_code = request.session.get(REFERRAL_CODE_SESSION_KEY, "")
    if not referral_code:
        return None

    click = None
    click_id = request.session.get(REFERRAL_CLICK_ID_SESSION_KEY)
    if click_id:
        click = ReferralClick.objects.select_related("consultant").filter(id=click_id).first()

    consultant = click.consultant if click else None
    if not consultant:
        consultant = ReferralConsultant.objects.filter(code=referral_code, is_active=True).first()

    if not consultant:
        return None

    if hasattr(inquiry, "referral_consultant"):
        inquiry.referral_consultant = consultant
    if hasattr(inquiry, "referral_click"):
        inquiry.referral_click = click
    if hasattr(inquiry, "referral_code"):
        inquiry.referral_code = consultant.code

    return click


def mark_referral_conversion(click, inquiry):
    if not click or click.converted_at:
        return

    click.converted_at = timezone.now()
    click.converted_model = inquiry._meta.label_lower
    click.converted_object_id = inquiry.pk
    click.save(update_fields=["converted_at", "converted_model", "converted_object_id"])
