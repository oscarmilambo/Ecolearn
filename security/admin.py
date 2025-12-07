from django.contrib import admin
from .models import Role, UserRole, AuditLog, EncryptedData, SecuritySettings, BackupRecord

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'updated_at']
    list_filter = ['name', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'assigned_by', 'assigned_at', 'is_active']
    list_filter = ['role', 'is_active', 'assigned_at']
    search_fields = ['user__username', 'role__name']
    readonly_fields = ['assigned_at']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource_type', 'ip_address', 'timestamp', 'success']
    list_filter = ['action', 'resource_type', 'success', 'timestamp']
    search_fields = ['user__username', 'resource_type', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(EncryptedData)
class EncryptedDataAdmin(admin.ModelAdmin):
    list_display = ['identifier', 'created_at', 'updated_at']
    search_fields = ['identifier']
    readonly_fields = ['created_at', 'updated_at', 'encrypted_data']

@admin.register(SecuritySettings)
class SecuritySettingsAdmin(admin.ModelAdmin):
    list_display = ['setting_name', 'description', 'updated_by', 'updated_at']
    search_fields = ['setting_name', 'description']
    readonly_fields = ['updated_at']

@admin.register(BackupRecord)
class BackupRecordAdmin(admin.ModelAdmin):
    list_display = ['backup_type', 'file_size', 'created_by', 'created_at', 'is_encrypted']
    list_filter = ['backup_type', 'is_encrypted', 'created_at']
    search_fields = ['file_path']
    readonly_fields = ['created_at', 'file_size', 'checksum']
    
    def has_change_permission(self, request, obj=None):
        return False