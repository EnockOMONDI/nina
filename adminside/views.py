from django.shortcuts import get_object_or_404, render
from django.db.models import Min, Q

from .models import Destination, Hotel, Package


def home(request):
    featured_packages = list(
        Package.objects.filter(active=True, is_featured=True).order_by("-created_at")[:8]
    )

    if len(featured_packages) < 8:
        existing_ids = [pkg.id for pkg in featured_packages]
        fallback_packages = (
            Package.objects.filter(active=True)
            .exclude(id__in=existing_ids)
            .order_by("-created_at")[: 8 - len(featured_packages)]
        )
        featured_packages.extend(fallback_packages)

    return render(
        request,
        'ninatoursui/pages/index.html',
        {"featured_packages": featured_packages},
    )


def packages(request):
    package_list = Package.objects.filter(active=True).order_by("-created_at")
    return render(request, 'ninatoursui/pages/packages.html', {"packages": package_list})


def package_detail(request, slug):
    package = get_object_or_404(Package, slug=slug, active=True)
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
        "availability_chips": availability_chips,
        "hotel_options": hotel_options,
        "package_inclusions": package_inclusions,
        "package_exclusions": package_exclusions,
        "inclusion_items": inclusion_items,
        "exclusion_items": exclusion_items,
    }
    return render(request, 'ninatoursui/pages/package-detail.html', context)


def hotels(request):
    hotel_list = Hotel.objects.filter(active=True).order_by("-created_at")
    return render(request, 'ninatoursui/pages/hotels.html', {"hotels": hotel_list})


def about(request):
    return render(request, 'ninatoursui/pages/aboutus.html')


def corporates(request):
    return render(request, 'ninatoursui/pages/corporate.html')


def destinations(request):
    selected_destination_slug = request.GET.get("destination", "").strip()
    destination_pills = Destination.objects.filter(active=True).order_by("sort_order", "name")
    visible_destinations = destination_pills
    if selected_destination_slug:
        visible_destinations = destination_pills.filter(slug=selected_destination_slug)

    base_qs = Package.objects.filter(active=True).select_related("destination")
    destinations_data = []
    for destination in visible_destinations:
        destination_packages = base_qs.filter(destination=destination)
        top_packages = list(destination_packages.order_by("price", "-created_at")[:2])
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
                "starting_from": destination_packages.aggregate(
                    starting_from=Min("price", filter=Q(is_featured=True, price__gt=0))
                )["starting_from"],
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
        },
    )


def contact(request):
    return render(request, 'pages/contact.html')
