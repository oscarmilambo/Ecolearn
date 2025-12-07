from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
import json

class Role(models.Model):
    """Define system roles with specific permissions"""
    ROLE_CHOICES = [
        ('admin', 'System Administrator'),
        ('moderator', 'Content Moderator'),
        ('analyst', 'Data Analyst'),
        ('health_officer', 'Health Officer'),
        ('emergency_responder', 'Emergency Responder'),
        ('user', 'Regular User'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField()
    permissions = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.get_name_display()

class UserRole(models.Model):
    """Assign roles to users"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='assigned_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user', 'role']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

class AuditLog(models.Model):
    """Track all system activities for security auditing"""
    ACTION_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('create', 'Create Record'),
        ('update', 'Update Record'),
        ('delete', 'Delete Record'),
        ('view', 'View Record'),
        ('export', 'Export Data'),
        ('import', 'Import Data'),
        ('alert_send', 'Emergency Alert Sent'),
        ('role_change', 'Role Assignment Change'),
        ('permission_change', 'Permission Change'),
        ('backup_create', 'Backup Created'),
        ('backup_restore', 'Backup Restored'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=100)  # Model name or resource type
    resource_id = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)
    success = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"

class EncryptedData(models.Model):
    """Store encrypted sensitive data"""
    identifier = models.CharField(max_length=255, unique=True)
    encrypted_data = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def encrypt_data(self, data):
        """Encrypt data using Fernet encryption"""
        key = settings.ENCRYPTION_KEY.encode()
        f = Fernet(key)
        self.encrypted_data = f.encrypt(json.dumps(data).encode())
    
    def decrypt_data(self):
        """Decrypt data"""
        key = settings.ENCRYPTION_KEY.encode()
        f = Fernet(key)
        decrypted = f.decrypt(self.encrypted_data)
        return json.loads(decrypted.decode())

class SecuritySettings(models.Model):
    """System-wide security settings"""
    setting_name = models.CharField(max_length=100, unique=True)
    setting_value = models.JSONField()
    description = models.TextField()
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.setting_name

class BackupRecord(models.Model):
    """Track system backups"""
    BACKUP_TYPES = [
        ('full', 'Full System Backup'),
        ('database', 'Database Backup'),
        ('media', 'Media Files Backup'),
        ('logs', 'Log Files Backup'),
    ]
    
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField()  # Size in bytes
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    checksum = models.CharField(max_length=64)  # SHA-256 checksum
    is_encrypted = models.BooleanField(default=True)
    retention_date = models.DateTimeField()  # When backup should be deleted
    
    def __str__(self):
        return f"{self.backup_type} - {self.created_at}"