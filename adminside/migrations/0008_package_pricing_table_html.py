from django.db import migrations
from django_ckeditor_5.fields import CKEditor5Field


def copy_option_table_to_package(apps, schema_editor):
    Package = apps.get_model("adminside", "Package")
    PackageHotelOption = apps.get_model("adminside", "PackageHotelOption")

    for package in Package.objects.all().iterator():
        option = (
            PackageHotelOption.objects.filter(package=package)
            .exclude(pricing_table_html="")
            .order_by("-is_recommended", "sort_order", "id")
            .first()
        )
        if option and not package.pricing_table_html:
            package.pricing_table_html = option.pricing_table_html
            package.save(update_fields=["pricing_table_html"])


class Migration(migrations.Migration):
    dependencies = [
        ("adminside", "0007_careerjob"),
    ]

    operations = [
        migrations.AddField(
            model_name="package",
            name="pricing_table_html",
            field=CKEditor5Field(blank=True, config_name="default", default=""),
        ),
        migrations.RunPython(copy_option_table_to_package, migrations.RunPython.noop),
    ]

