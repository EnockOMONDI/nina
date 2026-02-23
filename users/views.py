import logging
import threading

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from adminside.models import Hotel, Package, PackageHotelOption

from .forms import ContactForm, CorporateInquiryForm, PackageQuoteInquiryForm
from .tasks import send_contact_emails, send_corporate_emails, send_package_quote_emails

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
    return render(request, "pages/inquiry-success.html", {"inquiry_id": inquiry_id})


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
