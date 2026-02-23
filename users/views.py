import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from adminside.models import Package

from .forms import ContactForm, CorporateInquiryForm, PackageQuoteInquiryForm
from .tasks import send_contact_emails, send_corporate_emails, send_package_quote_emails

logger = logging.getLogger(__name__)


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            try:
                send_contact_emails(inquiry)
                logger.info("Contact inquiry %s emails sent successfully.", inquiry.id)
                return redirect(f"{reverse('inquiry-success')}?id={inquiry.id}")
            except Exception as exc:
                messages.warning(
                    request,
                    "Your request was received, but the confirmation email could not be sent. Our team will still contact you.",
                )
                logger.exception("Contact inquiry %s email send failed: %s", inquiry.id, exc)
                return redirect("contact")
        messages.error(request, "Please check the form and try again.")
        logger.warning("Contact form validation failed. Errors: %s", form.errors.as_json())
    else:
        form = ContactForm()

    return render(request, "pages/contact.html", {"form": form})


def corporate_view(request):
    if request.method == "POST":
        form = CorporateInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            try:
                send_corporate_emails(inquiry)
                logger.info("Corporate inquiry %s emails sent successfully.", inquiry.id)
                return redirect(f"{reverse('inquiry-success')}?id={inquiry.id}")
            except Exception as exc:
                messages.warning(
                    request,
                    "Your corporate inquiry was received, but the confirmation email could not be sent. Our team will still contact you.",
                )
                logger.exception("Corporate inquiry %s email send failed: %s", inquiry.id, exc)
                return redirect("corporates")
        messages.error(request, "Please check the form and try again.")
        logger.warning("Corporate form validation failed. Errors: %s", form.errors.as_json())
    else:
        form = CorporateInquiryForm()

    return render(request, "pages/corporates.html", {"form": form})


def inquiry_success_view(request):
    inquiry_id = request.GET.get("id", "").strip()
    return render(request, "pages/inquiry-success.html", {"inquiry_id": inquiry_id})


def package_quote_view(request):
    package = None
    package_slug = request.GET.get("package", "").strip()

    if request.method == "POST":
        form = PackageQuoteInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)

            posted_slug = form.cleaned_data.get("package_slug", "").strip()
            if posted_slug:
                package = Package.objects.filter(slug=posted_slug, active=True).first()
                if package:
                    inquiry.package = package

            inquiry.save()

            try:
                send_package_quote_emails(inquiry)
                logger.info("Package quote inquiry %s emails sent successfully.", inquiry.id)
                return redirect(f"{reverse('inquiry-success')}?id={inquiry.id}")
            except Exception as exc:
                messages.warning(
                    request,
                    "Your quote request was received, but the confirmation email could not be sent. Our team will still contact you.",
                )
                logger.exception("Package quote inquiry %s email send failed: %s", inquiry.id, exc)
                return redirect(f"{reverse('package-quote')}?package={posted_slug}" if posted_slug else "package-quote")

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
        form = PackageQuoteInquiryForm(initial=initial_data)

    context = {
        "form": form,
        "selected_package": package,
    }
    return render(request, "pages/package-quote.html", context)
