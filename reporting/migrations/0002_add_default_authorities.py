# Generated migration to add default authorities

from django.db import migrations


def create_default_authorities(apps, schema_editor):
    Authority = apps.get_model('reporting', 'Authority')
    
    # Create Lusaka City Council
    Authority.objects.get_or_create(
        name='Lusaka City Council (LCC)',
        defaults={
            'contact_email': 'environment@lcc.gov.zm',
            'contact_phone': '+260211253333',
            'coverage_areas': 'Lusaka, Kalingalinga, Kanyama, Chawama, Chelston, Woodlands',
            'is_active': True,
        }
    )
    
    # Create ZEMA
    Authority.objects.get_or_create(
        name='Zambia Environmental Management Agency (ZEMA)',
        defaults={
            'contact_email': 'info@zema.org.zm',
            'contact_phone': '+260211254023',
            'coverage_areas': 'Nationwide - All provinces',
            'is_active': True,
        }
    )
    
    # Create Lusaka Water and Sewerage Company
    Authority.objects.get_or_create(
        name='Lusaka Water and Sewerage Company (LWSC)',
        defaults={
            'contact_email': 'customercare@lwsc.co.zm',
            'contact_phone': '+260211222060',
            'coverage_areas': 'Lusaka water and sewerage areas',
            'is_active': True,
        }
    )


def remove_default_authorities(apps, schema_editor):
    Authority = apps.get_model('reporting', 'Authority')
    Authority.objects.filter(
        name__in=[
            'Lusaka City Council (LCC)',
            'Zambia Environmental Management Agency (ZEMA)',
            'Lusaka Water and Sewerage Company (LWSC)'
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_authorities, remove_default_authorities),
    ]
