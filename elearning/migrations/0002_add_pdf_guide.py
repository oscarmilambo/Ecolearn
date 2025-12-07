# Generated migration for adding PDF guide field to Module model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elearning', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='pdf_guide',
            field=models.FileField(blank=True, null=True, upload_to='module_pdfs/', verbose_name='PDF Guide'),
        ),
    ]
