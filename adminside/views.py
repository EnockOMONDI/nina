from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from users.forms import CareerApplicationForm
from users.testimonials import get_student_testimonials

from .models import CareerJob, Destination, Hotel, Package


def _resolve_market(request):
    selected_market = request.GET.get("market", "all").strip().lower()
    if selected_market not in {"all", "local", "international"}:
        selected_market = "all"
    return selected_market


def _attach_market_prices(packages):
    for pkg in packages:
        local_price = None
        international_price = None
        for price_row in pkg.market_prices.all():
            if not price_row.active:
                continue
            if price_row.market == "local":
                local_price = price_row
            elif price_row.market == "international":
                international_price = price_row
        pkg.local_market_price = local_price
        pkg.international_market_price = international_price
    return packages


def home(request):
    selected_market = _resolve_market(request)
    featured_packages = list(
        Package.objects.filter(active=True, is_featured=True)
        .prefetch_related("market_prices")
        .order_by("-created_at")[:8]
    )

    if len(featured_packages) < 8:
        existing_ids = [pkg.id for pkg in featured_packages]
        fallback_packages = (
            Package.objects.filter(active=True)
            .prefetch_related("market_prices")
            .exclude(id__in=existing_ids)
            .order_by("-created_at")[: 8 - len(featured_packages)]
        )
        featured_packages.extend(fallback_packages)

    featured_packages = list(_attach_market_prices(featured_packages))
    if selected_market in {"local", "international"}:
        filtered_packages = []
        for pkg in featured_packages:
            if selected_market == "local" and pkg.local_market_price:
                filtered_packages.append(pkg)
            if selected_market == "international" and pkg.international_market_price:
                filtered_packages.append(pkg)
        featured_packages = filtered_packages

    return render(
        request,
        'ninatoursui/pages/index.html',
        {
            "featured_packages": featured_packages,
            "selected_market": selected_market,
            "student_testimonials": get_student_testimonials(),
        },
    )


def packages(request):
    selected_market = _resolve_market(request)

    package_list = (
        Package.objects.filter(active=True)
        .prefetch_related("market_prices")
        .order_by("-created_at")
    )

    if selected_market in {"local", "international"}:
        package_list = package_list.filter(
            market_prices__market=selected_market,
            market_prices__active=True,
        ).distinct()

    package_list = list(package_list)
    package_list = list(_attach_market_prices(package_list))

    return render(
        request,
        'ninatoursui/pages/packages.html',
        {
            "packages": package_list,
            "selected_market": selected_market,
        },
    )


def package_detail(request, slug):
    selected_market = _resolve_market(request)
    package = get_object_or_404(
        Package.objects.filter(active=True).prefetch_related("market_prices"),
        slug=slug,
    )
    _attach_market_prices([package])

    display_price = None
    display_currency = ""
    if selected_market == "local" and package.local_market_price:
        display_price = package.local_market_price.amount
        display_currency = "KES"
    elif selected_market == "international" and package.international_market_price:
        display_price = package.international_market_price.amount
        display_currency = "USD"
    elif selected_market == "all":
        if package.local_market_price:
            display_price = package.local_market_price.amount
            display_currency = "KES"
        elif package.international_market_price:
            display_price = package.international_market_price.amount
            display_currency = "USD"
    if display_price is None and package.price and package.price > 0:
        display_price = package.price
        display_currency = "USD"
    availability_rows = list(
        package.availability_months.filter(active=True).order_by("year", "month", "sort_order", "id")
    )
    availability_chips = []
    for row in availability_rows:
        month_label = row.get_month_display()
        label = f"{month_label} {row.year}" if row.year else month_label
        availability_chips.append(
            {
                "label": label,
                "status": row.status,
                "notes": row.notes,
            }
        )

    hotel_options = list(
        package.hotel_options.filter(active=True)
        .select_related("hotel")
        .order_by("-is_recommended", "sort_order", "id")
    )
    package_pricing_table_html = package.pricing_table_html or ""
    if not package_pricing_table_html:
        first_option_with_table = next(
            (option for option in hotel_options if option.pricing_table_html),
            None,
        )
        if first_option_with_table:
            package_pricing_table_html = first_option_with_table.pricing_table_html

    package_inclusions = package.inclusions
    if not package_inclusions:
        first_with_inclusions = package.itinerary_days.exclude(inclusions="").order_by("sort_order", "day_number", "id").first()
        if first_with_inclusions:
            package_inclusions = first_with_inclusions.inclusions

    package_exclusions = package.exclusions
    if not package_exclusions:
        first_with_exclusions = package.itinerary_days.exclude(exclusions="").order_by("sort_order", "day_number", "id").first()
        if first_with_exclusions:
            package_exclusions = first_with_exclusions.exclusions

    inclusion_items = [item.strip() for item in (package_inclusions or "").splitlines() if item.strip()]
    exclusion_items = [item.strip() for item in (package_exclusions or "").splitlines() if item.strip()]

    context = {
        "package": package,
        "selected_market": selected_market,
        "display_price": display_price,
        "display_currency": display_currency,
        "availability_chips": availability_chips,
        "hotel_options": hotel_options,
        "package_pricing_table_html": package_pricing_table_html,
        "package_inclusions": package_inclusions,
        "package_exclusions": package_exclusions,
        "inclusion_items": inclusion_items,
        "exclusion_items": exclusion_items,
    }
    return render(request, 'ninatoursui/pages/package-detail.html', context)


def hotels(request):
    search_query = request.GET.get("q", "").strip()
    selected_city = request.GET.get("city", "").strip()
    selected_region = request.GET.get("region", "").strip()

    hotel_list = Hotel.objects.filter(active=True).order_by("name")
    if search_query:
        hotel_list = hotel_list.filter(name__icontains=search_query)
    if selected_city:
        hotel_list = hotel_list.filter(city__iexact=selected_city)
    if selected_region:
        hotel_list = hotel_list.filter(region__iexact=selected_region)

    cities = list(
        Hotel.objects.filter(active=True)
        .exclude(city="")
        .values_list("city", flat=True)
        .distinct()
        .order_by("city")
    )
    regions = list(
        Hotel.objects.filter(active=True)
        .exclude(region="")
        .values_list("region", flat=True)
        .distinct()
        .order_by("region")
    )

    return render(
        request,
        "ninatoursui/pages/hotels.html",
        {
            "hotels": hotel_list,
            "search_query": search_query,
            "selected_city": selected_city,
            "selected_region": selected_region,
            "cities": cities,
            "regions": regions,
        },
    )


def about(request):
    return render(request, 'ninatoursui/pages/aboutus.html')


def admin_tutorial(request):
    return render(request, "ninatoursui/pages/admin-tutorial.html")


def corporates(request):
    return render(request, 'ninatoursui/pages/corporate.html')


def destinations(request):
    selected_market = _resolve_market(request)
    selected_destination_slug = request.GET.get("destination", "").strip()
    destination_pills = Destination.objects.filter(active=True).order_by("sort_order", "name")
    visible_destinations = destination_pills
    if selected_destination_slug:
        visible_destinations = destination_pills.filter(slug=selected_destination_slug)

    base_qs = (
        Package.objects.filter(active=True)
        .select_related("destination")
        .prefetch_related("market_prices")
    )
    destinations_data = []
    for destination in visible_destinations:
        destination_packages = base_qs.filter(destination=destination)
        top_packages = list(destination_packages.order_by("price", "-created_at")[:2])
        top_packages = list(_attach_market_prices(top_packages))

        eligible_prices = []
        for pkg in destination_packages:
            local_price = None
            international_price = None
            for price_row in pkg.market_prices.all():
                if not price_row.active:
                    continue
                if price_row.market == "local":
                    local_price = price_row
                elif price_row.market == "international":
                    international_price = price_row

            if selected_market == "local":
                if local_price:
                    eligible_prices.append((local_price.amount, "KES"))
            elif selected_market == "international":
                if international_price:
                    eligible_prices.append((international_price.amount, "USD"))
            else:
                if local_price:
                    eligible_prices.append((local_price.amount, "KES"))
                elif international_price:
                    eligible_prices.append((international_price.amount, "USD"))
                elif pkg.price and pkg.price > 0:
                    eligible_prices.append((pkg.price, "USD"))

        for pkg in top_packages:
            pkg.hotel_options_count = pkg.hotel_options.filter(active=True).count()
            month_rows = pkg.availability_months.filter(active=True).order_by("year", "month", "sort_order", "id")
            month_labels = []
            for month_row in month_rows:
                month_name = month_row.get_month_display()
                month_labels.append(f"{month_name} {month_row.year}" if month_row.year else month_name)
            pkg.available_month_labels = month_labels[:4]
            pkg.available_month_extra_count = max(0, len(month_labels) - 4)

        destinations_data.append(
            {
                "name": destination.name,
                "slug": destination.slug,
                "package_count": destination_packages.count(),
                "starting_from": min(eligible_prices, key=lambda row: row[0])[0] if eligible_prices else None,
                "starting_from_currency": min(eligible_prices, key=lambda row: row[0])[1] if eligible_prices else "",
                "top_packages": top_packages,
            }
        )

    return render(
        request,
        "ninatoursui/pages/destinations.html",
        {
            "destinations": destinations_data,
            "destination_pills": destination_pills,
            "selected_destination_slug": selected_destination_slug,
            "selected_market": selected_market,
        },
    )


def contact(request):
    return render(request, 'ninatoursui/pages/contact.html')


def careers(request):
    selected_type = request.GET.get("type", "all").strip().lower()
    selected_status = request.GET.get("status", "all").strip().lower()

    jobs = CareerJob.objects.filter(active=True).order_by("sort_order", "-created_at")
    if selected_type != "all":
        jobs = jobs.filter(job_type=selected_type)
    if selected_status != "all":
        jobs = jobs.filter(status=selected_status)

    today = timezone.localdate()
    jobs = list(jobs)
    for job in jobs:
        deadline_open = not job.deadline or job.deadline >= today
        job.is_open_for_application = job.status == CareerJob.STATUS_OPEN and deadline_open
    application_form = CareerApplicationForm()

    context = {
        "jobs": jobs,
        "selected_type": selected_type,
        "selected_status": selected_status,
        "job_type_choices": CareerJob.JOB_TYPE_CHOICES,
        "job_status_choices": CareerJob.STATUS_CHOICES,
        "today": today,
        "application_form": application_form,
        "uploadcare_public_key": settings.UPLOADCARE_PUBLIC_KEY,
        "careers_max_file_size_mb": int(getattr(settings, "CAREERS_MAX_FILE_SIZE_BYTES", 10 * 1024 * 1024) / (1024 * 1024)),
    }
    return render(request, "ninatoursui/pages/careers.html", context)


def career_detail(request, slug):
    job = get_object_or_404(CareerJob.objects.filter(active=True), slug=slug)
    today = timezone.localdate()
    deadline_open = not job.deadline or job.deadline >= today
    job.is_open_for_application = job.status == CareerJob.STATUS_OPEN and deadline_open
    related_jobs = list(
        CareerJob.objects.filter(active=True)
        .exclude(id=job.id)
        .order_by("sort_order", "-created_at")[:3]
    )
    for related in related_jobs:
        related_deadline_open = not related.deadline or related.deadline >= today
        related.is_open_for_application = related.status == CareerJob.STATUS_OPEN and related_deadline_open
    application_form = CareerApplicationForm(selected_job=job)

    context = {
        "job": job,
        "related_jobs": related_jobs,
        "today": today,
        "application_form": application_form,
        "uploadcare_public_key": settings.UPLOADCARE_PUBLIC_KEY,
        "careers_max_file_size_mb": int(getattr(settings, "CAREERS_MAX_FILE_SIZE_BYTES", 10 * 1024 * 1024) / (1024 * 1024)),
    }
    return render(request, "ninatoursui/pages/career-detail.html", context)
