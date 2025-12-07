# Generated security migrations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('admin', 'System Administrator'), ('moderator', 'Content Moderator'), ('analyst', 'Data Analyst'), ('health_officer', 'Health Officer'), ('emergency_responder', 'Emergency Responder'), ('user', 'Regular User')], max_length=50, unique=True)),
                ('description', models.TextField()),
                ('permissions', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SecuritySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('setting_name', models.CharField(max_length=100, unique=True)),
                ('setting_value', models.JSONField()),
                ('description', models.TextField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EncryptedData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255, unique=True)),
                ('encrypted_data', models.BinaryField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='BackupRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('backup_type', models.CharField(choices=[('full', 'Full System Backup'), ('database', 'Database Backup'), ('media', 'Media Files Backup'), ('logs', 'Log Files Backup')], max_length=20)),
                ('file_path', models.CharField(max_length=500)),
                ('file_size', models.BigIntegerField()),
                ('checksum', models.CharField(max_length=64)),
                ('is_encrypted', models.BooleanField(default=True)),
                ('retention_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('login', 'User Login'), ('logout', 'User Logout'), ('create', 'Create Record'), ('update', 'Update Record'), ('delete', 'Delete Record'), ('view', 'View Record'), ('export', 'Export Data'), ('import', 'Import Data'), ('alert_send', 'Emergency Alert Sent'), ('role_change', 'Role Assignment Change'), ('permission_change', 'Permission Change'), ('backup_create', 'Backup Created'), ('backup_restore', 'Backup Restored')], max_length=50)),
                ('resource_type', models.CharField(max_length=100)),
                ('resource_id', models.CharField(blank=True, max_length=100, null=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('details', models.JSONField(default=dict)),
                ('success', models.BooleanField(default=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('assigned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_roles', to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='security.role')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_roles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='userrole',
            constraint=models.UniqueConstraint(fields=('user', 'role'), name='security_userrole_user_id_role_id_uniq'),
        ),
    ]