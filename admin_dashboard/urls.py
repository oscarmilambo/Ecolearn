# admin_dashboard/urls.py
from django.urls import path, include
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # User Management
    path('users/', views.user_management, name='users'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/demographics/', views.user_demographics, name='user_demographics'),
    path('export-users/', views.export_users, name='export_users'),
    
    # Content Management System (CMS)
    path('modules/', views.module_management, name='modules'),
    path('modules/create/', views.module_create, name='module_create'),
    path('modules/<int:module_id>/edit/', views.module_edit, name='module_edit'),
    path('modules/<int:module_id>/delete/', views.module_delete, name='module_delete'),
    path('modules/<int:module_id>/toggle-publish/', views.module_toggle_publish, name='module_toggle_publish'),
    path('modules/bulk-action/', views.module_bulk_publish, name='module_bulk_action'),
    path('modules/<int:module_id>/lessons/create/', views.lesson_create, name='lesson_create'),
    path('lessons/<int:lesson_id>/edit/', views.lesson_edit, name='lesson_edit'),
    path('lessons/<int:lesson_id>/delete/', views.lesson_delete, name='lesson_delete'),
    path('content/analytics/', views.content_analytics, name='content_analytics'),
    
    # Dumping Reports
    path('reports/', views.report_management, name='reports'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('authorities/', views.authority_management, name='authority_management'),
    path('export-reports/', views.export_reports, name='export_reports'),
    path('mark-resolved/<int:report_id>/', views.mark_resolved, name='mark_resolved'),
    path('notify-lcc/<int:report_id>/', views.notify_lcc, name='notify_lcc'),
    path('assign-team/<int:report_id>/', views.assign_team, name='assign_team'),
    
    # Community Forum Moderation
    path('forum/', views.forum_moderation, name='forum_moderation'),
    path('moderate/<str:content_type>/<int:content_id>/', views.moderate_content, name='moderate_content'),
    
    # Community Challenges Management
    path('challenges/', views.challenge_management, name='challenge_management'),
    path('challenges/create/', views.challenge_create, name='challenge_create'),
    path('challenges/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('challenges/<int:challenge_id>/delete/', views.challenge_delete, name='challenge_delete'),
    
    # Challenge Proof Management
    path('challenge-proofs/', views.challenge_proofs, name='challenge_proofs'),
    path('challenge-proofs/<int:proof_id>/approve/', views.proof_approve, name='proof_approve'),
    path('challenge-proofs/<int:proof_id>/reject/', views.proof_reject, name='proof_reject'),
    path('challenge-proofs/bulk-approve/', views.proof_bulk_approve, name='proof_bulk_approve'),
    
    # Notification System Management
    path('notifications/', views.notification_management, name='notification_management'),
    path('notifications/create/', views.notification_create, name='notification_create'),
    path('notifications/send/', views.notification_send, name='notification_send'),
    path('notifications/history/', views.notification_history, name='notification_history'),
    path('notifications/analytics/', views.notification_analytics, name='notification_analytics'),
    
    # Emergency Alert System
    path('alerts/', views.emergency_alerts, name='emergency_alerts'),
    path('alerts/create/', views.alert_create, name='alert_create'),
    path('alerts/<int:alert_id>/', views.alert_detail, name='alert_detail'),
    path('alerts/<int:alert_id>/send/', views.alert_send, name='alert_send'),
    path('alerts/<int:alert_id>/deactivate/', views.alert_deactivate, name='alert_deactivate'),
    path('priority-reports/', views.priority_reports, name='priority_reports'),
    path('escalate-report/<int:report_id>/', views.escalate_report, name='escalate_report'),
    
    # System Settings
    path('settings/', views.system_settings, name='settings'),
    
    # Security Management
    path('security/', include('security.urls')),
]
