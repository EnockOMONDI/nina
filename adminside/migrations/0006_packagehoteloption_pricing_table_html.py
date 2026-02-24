from django.db import migrations
import django_ckeditor_5.fields


SOPA_RATE_TABLE_HTML = """
<h4>Sopa Lodges - Land Cruiser Option (USD)</h4>
<table>
  <thead>
    <tr>
      <th>Season</th>
      <th>1 Pax</th>
      <th>2 Pax</th>
      <th>4 Pax</th>
      <th>6 Pax</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Green Season (01 Apr - 31 May)</td><td>2580</td><td>1760</td><td>1455</td><td>1350</td></tr>
    <tr><td>Mid Season (02 Jan - 31 Mar, 01 Nov - 21 Dec)</td><td>3375</td><td>2340</td><td>1965</td><td>1840</td></tr>
    <tr><td>Mid Season (01 Jun - 30 Jun)</td><td>2880</td><td>1990</td><td>1685</td><td>1580</td></tr>
    <tr><td>High Season (01 Jul - 31 Oct, 22 Dec - 01 Jan 2026)</td><td>3545</td><td>2540</td><td>2225</td><td>2120</td></tr>
  </tbody>
</table>

<h4>Sopa Lodges - Tour Van Option (USD)</h4>
<table>
  <thead>
    <tr>
      <th>Season</th>
      <th>1 Pax</th>
      <th>2 Pax</th>
      <th>4 Pax</th>
      <th>6 Pax</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Green Season (01 Apr - 31 May)</td><td>2110</td><td>1525</td><td>1335</td><td>1275</td></tr>
    <tr><td>Mid Season (02 Jan - 31 Mar, 01 Nov - 21 Dec)</td><td>2805</td><td>2060</td><td>1820</td><td>1745</td></tr>
    <tr><td>Mid Season (01 Jun - 30 Jun)</td><td>2470</td><td>1785</td><td>1580</td><td>1510</td></tr>
    <tr><td>High Season (01 Jul - 31 Oct, 22 Dec - 01 Jan 2026)</td><td>3230</td><td>2380</td><td>2145</td><td>2065</td></tr>
  </tbody>
</table>
"""


def seed_one_package_tables(apps, schema_editor):
    Package = apps.get_model("adminside", "Package")
    PackageHotelOption = apps.get_model("adminside", "PackageHotelOption")

    target_slugs = [
        "6-days-sopa-lodges-amboseli-naivasha-mara",
        "6-days-sopa-lodges-amboseli-naivasha-mara-2026",
    ]
    package = Package.objects.filter(slug__in=target_slugs).first()
    if not package:
        return

    options = PackageHotelOption.objects.filter(package=package, active=True)
    for option in options:
        option.pricing_table_html = SOPA_RATE_TABLE_HTML
        option.save(update_fields=["pricing_table_html"])


class Migration(migrations.Migration):

    dependencies = [
        ("adminside", "0005_packagemarketprice"),
    ]

    operations = [
        migrations.AddField(
            model_name="packagehoteloption",
            name="pricing_table_html",
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, config_name="default", default=""),
        ),
        migrations.RunPython(seed_one_package_tables, migrations.RunPython.noop),
    ]
