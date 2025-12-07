from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import UserRole, AuditLog

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Ensure we always return a valid IP address
    return ip if ip else '127.0.0.1'

def log_activity(user, action, resource_type, resource_id=None, details=None, success=True, request=None):
    """Log user activity for audit trail"""
    ip_address = '127.0.0.1'
    user_agent = 'Unknown'
    
    if request:
        ip_address = get_client_ip(request) or '127.0.0.1'
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    
    # Ensure ip_address is never None
    if not ip_address:
        ip_address = '127.0.0.1'
    
    AuditLog.objects.create(
        user=user,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details or {},
        success=success
    )

def has_permission(user, permission):
    """Check if user has specific permission"""
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    user_roles = UserRole.objects.filter(user=user, is_active=True)
    for user_role in user_roles:
        role_permissions = user_role.role.permissions
        if permission in role_permissions and role_permissions[permission]:
            return True
    
    return False

def require_permission(permission):
    """Decorator to require specific permission"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not has_permission(request.user, permission):
                log_activity(
                    request.user,
                    'permission_denied',
                    'view_access',
                    details={'permission': permission, 'view': view_func.__name__},
                    success=False,
                    request=request
                )
                
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'error': 'Permission denied'}, status=403)
                
                messages.error(request, 'You do not have permission to access this resource.')
                return redirect('admin_dashboard:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_role(role_name):
    """Decorator to require specific role"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            user_roles = UserRole.objects.filter(
                user=request.user,
                role__name=role_name,
                is_active=True
            )
            
            if not user_roles.exists():
                log_activity(
                    request.user,
                    'role_denied',
                    'view_access',
                    details={'required_role': role_name, 'view': view_func.__name__},
                    success=False,
                    request=request
                )
                
                messages.error(request, f'You need {role_name} role to access this resource.')
                return redirect('admin_dashboard:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Permission constants
PERMISSIONS = {
    'view_dashboard': 'View Admin Dashboard',
    'manage_users': 'Manage Users',
    'manage_content': 'Manage Content',
    'manage_reports': 'Manage Reports',
    'send_alerts': 'Send Emergency Alerts',
    'view_analytics': 'View Analytics',
    'manage_roles': 'Manage User Roles',
    'view_audit_logs': 'View Audit Logs',
    'manage_backups': 'Manage System Backups',
    'manage_security': 'Manage Security Settings',
    'export_data': 'Export System Data',
    'import_data': 'Import System Data',
    'moderate_content': 'Moderate User Content',
    'manage_challenges': 'Manage Challenges',
    'manage_notifications': 'Manage Notifications',
}

# Default role permissions
DEFAULT_ROLE_PERMISSIONS = {
    'admin': {
        'view_dashboard': True,
        'manage_users': True,
        'manage_content': True,
        'manage_reports': True,
        'send_alerts': True,
        'view_analytics': True,
        'manage_roles': True,
        'view_audit_logs': True,
        'manage_backups': True,
        'manage_security': True,
        'export_data': True,
        'import_data': True,
        'moderate_content': True,
        'manage_challenges': True,
        'manage_notifications': True,
    },
    'moderator': {
        'view_dashboard': True,
        'manage_content': True,
        'manage_reports': True,
        'view_analytics': True,
        'moderate_content': True,
        'manage_challenges': True,
    },
    'analyst': {
        'view_dashboard': True,
        'view_analytics': True,
        'export_data': True,
    },
    'health_officer': {
        'view_dashboard': True,
        'manage_reports': True,
        'send_alerts': True,
        'view_analytics': True,
    },
    'emergency_responder': {
        'view_dashboard': True,
        'send_alerts': True,
        'manage_reports': True,
    },
    'user': {
        'view_dashboard': False,
    }
}