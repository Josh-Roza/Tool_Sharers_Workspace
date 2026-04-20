from django.db import migrations

def seed_categories(apps, schema_editor):
    Category = apps.get_model('Tool_Sharers_App', 'Category')

    categories = [
        "Power Tools",
        "Hand Tools",
        "Lawn & Garden",
        "Automotive",
        "Painting",
        "Plumbing",
        "Electrical",
        "Cleaning",
        "Woodworking",
        "Miscellaneous",
    ]

    for name in categories:
        Category.objects.get_or_create(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ('Tool_Sharers_App', '0003_user_paypal_email_user_preferred_payment_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_categories),
    ]