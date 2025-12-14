# Generated manually for social media fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collaboration', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cleanupgroup',
            name='facebook_url',
            field=models.URLField(blank=True, help_text='Facebook page or group URL'),
        ),
        migrations.AddField(
            model_name='cleanupgroup',
            name='whatsapp_url',
            field=models.URLField(blank=True, help_text='WhatsApp group invite link'),
        ),
        migrations.AddField(
            model_name='cleanupgroup',
            name='twitter_url',
            field=models.URLField(blank=True, help_text='Twitter/X profile URL'),
        ),
        migrations.AddField(
            model_name='cleanupgroup',
            name='linkedin_url',
            field=models.URLField(blank=True, help_text='LinkedIn page URL'),
        ),
        migrations.AddField(
            model_name='cleanupgroup',
            name='instagram_url',
            field=models.URLField(blank=True, help_text='Instagram profile URL'),
        ),
        migrations.AddField(
            model_name='cleanupgroup',
            name='youtube_url',
            field=models.URLField(blank=True, help_text='YouTube channel URL'),
        ),
        migrations.AddField(
            model_name='cleanupgroup',
            name='website_url',
            field=models.URLField(blank=True, help_text='Group website or blog'),
        ),
    ]