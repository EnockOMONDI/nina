from decimal import Decimal

from django.db import migrations, models


def seed_international_prices(apps, schema_editor):
    Package = apps.get_model("adminside", "Package")
    PackageMarketPrice = apps.get_model("adminside", "PackageMarketPrice")

    packages = Package.objects.filter(active=True)
    for package in packages:
        base_price = package.price or Decimal("0.00")
        if base_price <= 0:
            continue

        PackageMarketPrice.objects.update_or_create(
            package=package,
            market="international",
            defaults={
                "currency": "USD",
                "amount": base_price,
                "notes": "Seeded from base package price.",
                "active": True,
                "sort_order": 2,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("adminside", "0004_package_exclusions_package_inclusions"),
    ]

    operations = [
        migrations.CreateModel(
            name="PackageMarketPrice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "market",
                    models.CharField(
                        choices=[("local", "Local"), ("international", "International")],
                        max_length=20,
                    ),
                ),
                (
                    "currency",
                    models.CharField(
                        choices=[("KES", "KES"), ("USD", "USD")],
                        max_length=3,
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("notes", models.CharField(blank=True, default="", max_length=200)),
                ("active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "package",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="market_prices", to="adminside.package"),
                ),
            ],
            options={
                "ordering": ["sort_order", "id"],
                "constraints": [
                    models.UniqueConstraint(fields=("package", "market"), name="uniq_package_market_price_market")
                ],
            },
        ),
        migrations.RunPython(seed_international_prices, migrations.RunPython.noop),
    ]
