from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()
from .models import Role, UserRole, AuditLog, SecuritySettings, BackupRecord
from .permissions import require_permission, log_activity, DEFAULT_ROLE_PERMISSIONS
from .backup import BackupManager
import json

@login_required
@require_permission('manage_security')
def security_dashboard(request):
    """Security management dashboard"""
    # Get recent security events
    recent_logs = AuditLog.objects.filter(
        timestamp__gte=timezone.now() - timedelta(days=7)
    ).order_by('-timestamp')[:10]
    
    # Get security statistics
    stats = {
        'total_users': User.objects.count(),
        'active_sessions': AuditLog.objects.filter(
            action='login',
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).count(),
        'failed_attempts': AuditLog.objects.filter(
            success=False,
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).count(),
        'recent_backups': BackupRecord.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count(),
    }
    
    # Get backup status
    backup_manager = BackupManager()
    backup_status = backup_manager.get_backup_status()
    
    context = {
        'recent_logs': recent_logs,
        'stats': stats,
        'backup_status': backup_status,
    }
    
    log_activity(
        request.user,
        'view',
        'security_dashboard',
        request=request
    )
    
    return render(request, 'security/dashboard.html', context)

@login_required
@require_permission('manage_roles')
def role_management(request):
    """Manage user roles and permissions"""
    roles = Role.objects.all().order_by('name')
    users_with_roles = User.objects.prefetch_related('user_roles__role').all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'assign_role':
            user_id = request.POST.get('user_id')
            role_id = request.POST.get('role_id')
            
            try:
                user = User.objects.get(id=user_id)
                role = Role.objects.get(id=role_id)
                
                user_role, created = UserRole.objects.get_or_create(
                    user=user,
                    role=role,
                    defaults={'assigned_by': request.user}
                )
                
                if created:
                    messages.success(request, f'Role {role.name} assigned to {user.username}')
                    log_activity(
                        request.user,
                        'role_change',
                        'user_role',
                        resource_id=user.id,
                        details={'action': 'assign', 'role': role.name},
                        request=request
                    )
                else:
                    messages.info(request, f'{user.username} already has {role.name} role')
                    
            except (User.DoesNotExist, Role.DoesNotExist):
                messages.error(request, 'Invalid user or role')
        
        elif action == 'remove_role':
            user_role_id = request.POST.get('user_role_id')
            
            try:
                user_role = UserRole.objects.get(id=user_role_id)
                user = user_role.user
                role = user_role.role
                
                user_role.delete()
                
                messages.success(request, f'Role {role.name} removed from {user.username}')
                log_activity(
                    request.user,
                    'role_change',
                    'user_role',
                    resource_id=user.id,
                    details={'action': 'remove', 'role': role.name},
                    request=request
                )
                
            except UserRole.DoesNotExist:
                messages.error(request, 'Invalid role assignment')
        
        return redirect('admin_dashboard:security:role_management')
    
    context = {
        'roles': roles,
        'users_with_roles': users_with_roles,
    }
    
    return render(request, 'security/role_management.html', context)

@login_required
@require_permission('view_audit_logs')
def audit_logs(request):
    """View audit logs"""
    logs = AuditLog.objects.all().order_by('-timestamp')
    
    # Filter by user
    user_filter = request.GET.get('user')
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    
    # Filter by action
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        logs = logs.filter(timestamp__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__lte=date_to)
    
    # Filter by success/failure
    success_filter = request.GET.get('success')
    if success_filter in ['true', 'false']:
        logs = logs.filter(success=success_filter == 'true')
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get available actions for filter
    actions = AuditLog.objects.values_list('action', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'actions': actions,
        'filters': {
            'user': user_filter,
            'action': action_filter,
            'date_from': date_from,
            'date_to': date_to,
            'success': success_filter,
        }
    }
    
    log_activity(
        request.user,
        'view',
        'audit_logs',
        request=request
    )
    
    return render(request, 'security/audit_logs.html', context)

@login_required
@require_permission('manage_backups')
def backup_management(request):
    """Manage system backups"""
    backups = BackupRecord.objects.all().order_by('-created_at')
    backup_manager = BackupManager()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_backup':
            backup_type = request.POST.get('backup_type')
            
            try:
                if backup_type == 'full':
                    backup = backup_manager.create_full_backup(request.user)
                elif backup_type == 'database':
                    backup = backup_manager.create_database_backup(request.user)
                elif backup_type == 'media':
                    backup = backup_manager.create_media_backup(request.user)
                elif backup_type == 'logs':
                    backup = backup_manager.create_logs_backup(request.user)
                else:
                    messages.error(request, 'Invalid backup type')
                    return redirect('admin_dashboard:security:backup_management')
                
                messages.success(request, f'{backup_type.title()} backup created successfully')
                log_activity(
                    request.user,
                    'backup_create',
                    'system_backup',
                    resource_id=backup.id,
                    details={'backup_type': backup_type},
                    request=request
                )
                
            except Exception as e:
                messages.error(request, f'Backup failed: {str(e)}')
        
        elif action == 'restore_backup':
            backup_id = request.POST.get('backup_id')
            
            try:
                backup = BackupRecord.objects.get(id=backup_id)
                
                if backup.backup_type == 'database':
                    backup_manager.restore_database_backup(backup, request.user)
                    messages.success(request, 'Database restored successfully')
                    log_activity(
                        request.user,
                        'backup_restore',
                        'system_backup',
                        resource_id=backup.id,
                        details={'backup_type': backup.backup_type},
                        request=request
                    )
                else:
                    messages.error(request, 'Only database backups can be restored automatically')
                
            except BackupRecord.DoesNotExist:
                messages.error(request, 'Backup not found')
            except Exception as e:
                messages.error(request, f'Restore failed: {str(e)}')
        
        elif action == 'cleanup_backups':
            try:
                backup_manager.cleanup_old_backups()
                messages.success(request, 'Old backups cleaned up successfully')
                log_activity(
                    request.user,
                    'backup_cleanup',
                    'system_maintenance',
                    request=request
                )
            except Exception as e:
                messages.error(request, f'Cleanup failed: {str(e)}')
        
        return redirect('admin_dashboard:security:backup_management')
    
    # Get backup statistics
    backup_stats = {
        'total_backups': backups.count(),
        'total_size': sum(backup.file_size for backup in backups),
        'recent_backups': backups.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count(),
    }
    
    # Pagination
    paginator = Paginator(backups, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'backup_stats': backup_stats,
    }
    
    return render(request, 'security/backup_management.html', context)

@login_required
@require_permission('manage_security')
def security_settings(request):
    """Manage security settings"""
    settings_list = SecuritySettings.objects.all().order_by('setting_name')
    
    if request.method == 'POST':
        setting_name = request.POST.get('setting_name')
        setting_value = request.POST.get('setting_value')
        description = request.POST.get('description')
        
        try:
            # Parse JSON value
            parsed_value = json.loads(setting_value)
            
            setting, created = SecuritySettings.objects.get_or_create(
                setting_name=setting_name,
                defaults={
                    'setting_value': parsed_value,
                    'description': description,
                    'updated_by': request.user
                }
            )
            
            if not created:
                setting.setting_value = parsed_value
                setting.description = description
                setting.updated_by = request.user
                setting.save()
            
            action = 'create' if created else 'update'
            messages.success(request, f'Security setting {action}d successfully')
            log_activity(
                request.user,
                'update',
                'security_settings',
                resource_id=setting.id,
                details={'setting_name': setting_name, 'action': action},
                request=request
            )
            
        except json.JSONDecodeError:
            messages.error(request, 'Invalid JSON format in setting value')
        except Exception as e:
            messages.error(request, f'Error saving setting: {str(e)}')
        
        return redirect('admin_dashboard:security:security_settings')
    
    context = {
        'settings_list': settings_list,
    }
    
    return render(request, 'security/security_settings.html', context)

@login_required
@require_permission('manage_roles')
def initialize_roles(request):
    """Initialize default roles and permissions"""
    if request.method == 'POST':
        try:
            for role_name, permissions in DEFAULT_ROLE_PERMISSIONS.items():
                role, created = Role.objects.get_or_create(
                    name=role_name,
                    defaults={
                        'description': f'Default {role_name} role',
                        'permissions': permissions
                    }
                )
                
                if not created:
                    role.permissions = permissions
                    role.save()
            
            messages.success(request, 'Default roles initialized successfully')
            log_activity(
                request.user,
                'create',
                'role_initialization',
                details={'roles_count': len(DEFAULT_ROLE_PERMISSIONS)},
                request=request
            )
            
        except Exception as e:
            messages.error(request, f'Error initializing roles: {str(e)}')
    
    return redirect('admin_dashboard:security:role_management')

@login_required
@require_permission('view_audit_logs')
def export_audit_logs(request):
    """Export audit logs to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Timestamp', 'User', 'Action', 'Resource Type', 'Resource ID',
        'IP Address', 'Success', 'Details'
    ])
    
    logs = AuditLog.objects.all().order_by('-timestamp')
    
    for log in logs:
        writer.writerow([
            log.timestamp,
            log.user.username if log.user else 'Anonymous',
            log.get_action_display(),
            log.resource_type,
            log.resource_id,
            log.ip_address,
            'Yes' if log.success else 'No',
            json.dumps(log.details)
        ])
    
    log_activity(
        request.user,
        'export',
        'audit_logs',
        details={'format': 'csv'},
        request=request
    )
    
    return response