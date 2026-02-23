from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Min, Q

from .models import Hotel, Package


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
    return render(request, 'pages/packages.html', {"packages": package_list})


def package_detail(request, slug):
    package = get_object_or_404(Package, slug=slug, active=True)
    return render(request, 'ninatoursui/pages/package-detail.html', {"package": package})


def hotels(request):
    hotel_list = Hotel.objects.filter(active=True).order_by("-created_at")
    return render(request, 'pages/hotels.html', {"hotels": hotel_list})


def about(request):
    return render(request, 'pages/aboutus.html')


def corporates(request):
    return render(request, 'pages/corporates.html')


def destinations(request):
    base_qs = Package.objects.filter(active=True).exclude(location="")
    destination_rows = (
        base_qs.values("location")
        .annotate(
            package_count=Count("id"),
            starting_from=Min("price", filter=Q(is_featured=True, price__gt=0)),
        )
        .order_by("location")
    )

    destinations_data = []
    for row in destination_rows:
        location = row["location"]
        top_packages = list(
            base_qs.filter(location=location)
            .order_by("price", "-created_at")[:2]
        )
        destinations_data.append(
            {
                "location": location,
                "package_count": row["package_count"],
                "starting_from": row["starting_from"],
                "top_packages": top_packages,
            }
        )

    return render(request, "pages/destinations.html", {"destinations": destinations_data})


def contact(request):
    return render(request, 'pages/contact.html')
