# Remove unused social media fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collaboration', '0002_add_social_media_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cleanupgroup',
            name='linkedin_url',
        ),
        migrations.RemoveField(
            model_name='cleanupgroup',
            name='instagram_url',
        ),
        migrations.RemoveField(
            model_name='cleanupgroup',
            name='youtube_url',
        ),
        migrations.RemoveField(
            model_name='cleanupgroup',
            name='website_url',
        ),
    ]