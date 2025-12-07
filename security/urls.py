from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    path('', views.security_dashboard, name='dashboard'),
    path('roles/', views.role_management, name='role_management'),
    path('roles/initialize/', views.initialize_roles, name='initialize_roles'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('audit-logs/export/', views.export_audit_logs, name='export_audit_logs'),
    path('backups/', views.backup_management, name='backup_management'),
    path('settings/', views.security_settings, name='security_settings'),
]