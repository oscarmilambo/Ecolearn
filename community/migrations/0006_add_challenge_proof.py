# Generated migration for ChallengeProof model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('community', '0005_notificationlog_socialshare'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='challengeparticipant',
            options={'ordering': ['-contribution']},
        ),
        migrations.AlterField(
            model_name='challengeparticipant',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.CreateModel(
            name='ChallengeProof',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('before_photo', models.ImageField(help_text='Required: Before photo', upload_to='challenge_proofs/before/')),
                ('after_photo', models.ImageField(blank=True, help_text='Optional: After photo', null=True, upload_to='challenge_proofs/after/')),
                ('bags_collected', models.PositiveIntegerField(default=0, help_text='Number of bags collected')),
                ('description', models.TextField(blank=True, help_text='Optional description')),
                ('status', models.CharField(choices=[('pending', 'Pending Review'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('points_awarded', models.PositiveIntegerField(default=0, editable=False)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('admin_notes', models.TextField(blank=True)),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proofs', to='community.challengeparticipant')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_proofs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-submitted_at'],
            },
        ),
        migrations.AddIndex(
            model_name='challengeparticipant',
            index=models.Index(fields=['challenge', '-contribution'], name='community_c_challen_8e7c8a_idx'),
        ),
        migrations.AddIndex(
            model_name='challengeproof',
            index=models.Index(fields=['status', '-submitted_at'], name='community_c_status_9a2b3c_idx'),
        ),
    ]
