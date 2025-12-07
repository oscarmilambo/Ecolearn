from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .permissions import log_activity, get_client_ip
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware(MiddlewareMixin):
    """Middleware for security monitoring and logging"""
    
    def process_request(self, request):
        """Process incoming requests for security monitoring"""
        # Log suspicious activity patterns
        self.check_suspicious_patterns(request)
        
        # Add security headers
        return None
    
    def process_response(self, request, response):
        """Add security headers to response"""
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add CSP header for admin pages
        if request.path.startswith('/admin/') or request.path.startswith('/admin_dashboard/'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self';"
            )
        
        return response
    
    def check_suspicious_patterns(self, request):
        """Check for suspicious activity patterns"""
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Check for common attack patterns
        suspicious_patterns = [
            'union select',
            'drop table',
            'script>',
            'javascript:',
            '../',
            '..\\',
            'cmd.exe',
            '/etc/passwd',
            'base64_decode',
        ]
        
        request_data = str(request.GET) + str(request.POST) + request.path
        
        for pattern in suspicious_patterns:
            if pattern.lower() in request_data.lower():
                logger.warning(
                    f"Suspicious activity detected from {ip_address}: {pattern} in {request.path}"
                )
                
                # Log the suspicious activity
                if hasattr(request, 'user') and request.user.is_authenticated:
                    log_activity(
                        request.user,
                        'suspicious_activity',
                        'security_alert',
                        details={
                            'pattern': pattern,
                            'path': request.path,
                            'user_agent': user_agent
                        },
                        success=False,
                        request=request
                    )
                break

class AuditMiddleware(MiddlewareMixin):
    """Middleware for comprehensive audit logging"""
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Log view access for audit trail"""
        if request.user.is_authenticated:
            # Only log admin and sensitive views
            if (request.path.startswith('/admin/') or 
                request.path.startswith('/admin_dashboard/') or
                request.path.startswith('/api/')):
                
                log_activity(
                    request.user,
                    'view',
                    'page_access',
                    resource_id=request.path,
                    details={
                        'view_name': view_func.__name__,
                        'method': request.method,
                        'args': str(view_args),
                        'kwargs': str(view_kwargs)
                    },
                    request=request
                )
        
        return None

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login events"""
    log_activity(
        user,
        'login',
        'authentication',
        details={
            'login_method': 'standard',
            'session_key': request.session.session_key
        },
        request=request
    )
    
    logger.info(f"User {user.username} logged in from {get_client_ip(request)}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout events"""
    if user:
        log_activity(
            user,
            'logout',
            'authentication',
            details={
                'logout_method': 'standard'
            },
            request=request
        )
        
        logger.info(f"User {user.username} logged out from {get_client_ip(request)}")

class RateLimitMiddleware(MiddlewareMixin):
    """Simple rate limiting middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_counts = {}  # In production, use Redis or database
        super().__init__(get_response)
    
    def process_request(self, request):
        """Check rate limits"""
        ip_address = get_client_ip(request)
        current_time = timezone.now()
        
        # Clean old entries (older than 1 hour)
        cutoff_time = current_time - timezone.timedelta(hours=1)
        self.request_counts = {
            ip: timestamps for ip, timestamps in self.request_counts.items()
            if any(ts > cutoff_time for ts in timestamps)
        }
        
        # Update timestamps for current IP
        if ip_address not in self.request_counts:
            self.request_counts[ip_address] = []
        
        # Remove old timestamps for this IP
        self.request_counts[ip_address] = [
            ts for ts in self.request_counts[ip_address]
            if ts > cutoff_time
        ]
        
        # Add current request
        self.request_counts[ip_address].append(current_time)
        
        # Check if rate limit exceeded (100 requests per hour)
        if len(self.request_counts[ip_address]) > 100:
            logger.warning(f"Rate limit exceeded for IP: {ip_address}")
            
            # Log rate limit violation
            if hasattr(request, 'user') and request.user.is_authenticated:
                log_activity(
                    request.user,
                    'rate_limit_exceeded',
                    'security_alert',
                    details={
                        'request_count': len(self.request_counts[ip_address]),
                        'time_window': '1 hour'
                    },
                    success=False,
                    request=request
                )
        
        return None