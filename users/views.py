import logging
import threading

from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from adminside.models import CareerJob, Hotel, Package, PackageHotelOption

from .forms import CareerApplicationForm, ContactForm, CorporateInquiryForm, PackageQuoteInquiryForm
from .tasks import (
    send_career_application_emails,
    send_contact_emails,
    send_corporate_emails,
    send_package_quote_emails,
)

logger = logging.getLogger(__name__)


def _dispatch_email_async(send_fn, inquiry, label):
    def _runner():
        try:
            send_fn(inquiry)
            logger.info("%s %s emails sent successfully.", label, inquiry.id)
        except Exception:
            logger.exception("%s %s email send failed.", label, inquiry.id)

    threading.Thread(target=_runner, daemon=True).start()


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            _dispatch_email_async(send_contact_emails, inquiry, "Contact inquiry")
            return redirect(f"{reverse('inquiry-success')}?id={inquiry.id}")
        messages.error(request, "Please check the form and try again.")
        logger.warning("Contact form validation failed. Errors: %s", form.errors.as_json())
    else:
        form = ContactForm()

    return render(request, "ninatoursui/pages/contact.html", {"form": form})


def corporate_view(request):
    if request.method == "POST":
        form = CorporateInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            _dispatch_email_async(send_corporate_emails, inquiry, "Corporate inquiry")
            return redirect(f"{reverse('inquiry-success')}?id={inquiry.id}")
        messages.error(request, "Please check the form and try again.")
        logger.warning("Corporate form validation failed. Errors: %s", form.errors.as_json())
    else:
        form = CorporateInquiryForm()

    return render(request, "ninatoursui/pages/corporate.html", {"form": form})


def inquiry_success_view(request):
    inquiry_id = request.GET.get("id", "").strip()
    return render(request, "ninatoursui/pages/inquiry-success.html", {"inquiry_id": inquiry_id})


def package_quote_view(request):
    package = None
    package_slug = request.GET.get("package", "").strip()

    if request.method == "POST":
        posted_slug = request.POST.get("package_slug", "").strip()
        if posted_slug:
            package = Package.objects.filter(slug=posted_slug, active=True).first()

        form = PackageQuoteInquiryForm(request.POST, package=package)
        if form.is_valid():
            inquiry = form.save(commit=False)

            posted_slug = form.cleaned_data.get("package_slug", "").strip()
            if posted_slug:
                package = Package.objects.filter(slug=posted_slug, active=True).first()
                if package:
                    inquiry.package = package

            selected_hotel_option_id = form.cleaned_data.get("hotel_option", "").strip()
            if selected_hotel_option_id:
                selected_hotel_text = ""
                if selected_hotel_option_id.startswith("hotel:"):
                    hotel_id = selected_hotel_option_id.split(":", 1)[1]
                    selected_hotel = Hotel.objects.filter(id=hotel_id, active=True).first()
                    if selected_hotel:
                        selected_hotel_text = f"Selected hotel option: {selected_hotel.name}"
                elif package:
                    selected_option = (
                        PackageHotelOption.objects.filter(
                            id=selected_hotel_option_id,
                            package=package,
                            active=True,
                        )
                        .select_related("hotel")
                        .first()
                    )
                    if selected_option:
                        detail_parts = [selected_option.hotel.name]
                        if selected_option.room_type:
                            detail_parts.append(selected_option.room_type)
                        if selected_option.board_basis:
                            detail_parts.append(selected_option.board_basis)
                        if selected_option.nights:
                            detail_parts.append(f"{selected_option.nights} nights")
                        selected_hotel_text = f"Selected hotel option: {' | '.join(detail_parts)}"

                if selected_hotel_text:
                    inquiry.special_requests = (
                        f"{selected_hotel_text}\n{inquiry.special_requests}".strip()
                        if inquiry.special_requests
                        else selected_hotel_text
                    )

            inquiry.save()

            _dispatch_email_async(send_package_quote_emails, inquiry, "Package quote inquiry")
            return redirect(f"{reverse('inquiry-success')}?id={inquiry.id}")

        messages.error(request, "Please check the quote form and try again.")
        logger.warning("Package quote form validation failed. Errors: %s", form.errors.as_json())
    else:
        if not package_slug:
            messages.info(request, "Please choose a package before requesting a quote.")
            return redirect("packages")

        if package_slug:
            package = get_object_or_404(Package, slug=package_slug, active=True)

        initial_data = {}
        if package:
            initial_data = {
                "package_title": package.title,
                "package_slug": package.slug,
                "package_location": package.location,
                "package_duration": package.duration,
                "package_price": package.price,
            }
        form = PackageQuoteInquiryForm(initial=initial_data, package=package)

    context = {
        "form": form,
        "selected_package": package,
    }
    return render(request, "ninatoursui/pages/package-quote.html", context)


def career_application_submit_view(request):
    if request.method != "POST":
        return redirect("careers")

    form = CareerApplicationForm(request.POST)
    if form.is_valid():
        application = form.save()
        _dispatch_email_async(send_career_application_emails, application, "Career application")
        messages.success(request, "Your application has been received. We will get back to you soon.")
        return redirect(f"{reverse('career-detail', kwargs={'slug': application.job.slug})}#apply")

    messages.error(request, "Please check the application form and try again.")
    logger.warning("Career application form validation failed. Errors: %s", form.errors.as_json())
    today = timezone.localdate()
    selected_job = None
    posted_job_id = request.POST.get("job", "").strip()
    if posted_job_id.isdigit():
        selected_job = CareerJob.objects.filter(id=int(posted_job_id), active=True).first()

    if selected_job:
        selected_job.is_open_for_application = (
            selected_job.status == CareerJob.STATUS_OPEN
            and (not selected_job.deadline or selected_job.deadline >= today)
        )
        related_jobs = list(
            CareerJob.objects.filter(active=True)
            .exclude(id=selected_job.id)
            .order_by("sort_order", "-created_at")[:3]
        )
        for related in related_jobs:
            related.is_open_for_application = (
                related.status == CareerJob.STATUS_OPEN
                and (not related.deadline or related.deadline >= today)
            )
        return render(
            request,
            "ninatoursui/pages/career-detail.html",
            {
                "job": selected_job,
                "related_jobs": related_jobs,
                "today": today,
                "application_form": form,
                "uploadcare_public_key": settings.UPLOADCARE_PUBLIC_KEY,
                "careers_max_file_size_mb": int(getattr(settings, "CAREERS_MAX_FILE_SIZE_BYTES", 10 * 1024 * 1024) / (1024 * 1024)),
            },
        )

    jobs = list(CareerJob.objects.filter(active=True).order_by("sort_order", "-created_at"))
    for job in jobs:
        job.is_open_for_application = (
            job.status == CareerJob.STATUS_OPEN
            and (not job.deadline or job.deadline >= today)
        )

    return render(
        request,
        "ninatoursui/pages/careers.html",
        {
            "jobs": jobs,
            "selected_type": "all",
            "selected_status": "all",
            "job_type_choices": CareerJob.JOB_TYPE_CHOICES,
            "job_status_choices": CareerJob.STATUS_CHOICES,
            "today": timezone.localdate(),
            "application_form": form,
            "uploadcare_public_key": settings.UPLOADCARE_PUBLIC_KEY,
            "careers_max_file_size_mb": int(getattr(settings, "CAREERS_MAX_FILE_SIZE_BYTES", 10 * 1024 * 1024) / (1024 * 1024)),
        },
    )
