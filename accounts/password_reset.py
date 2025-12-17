"""
Password Reset Security System
Handles forgot password functionality with email and SMS options
"""

import secrets
import string
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .models import CustomUser

class PasswordResetService:
    """Service for handling password reset operations"""
    
    def __init__(self):
        self.token_expiry_hours = 1  # Reset tokens expire in 1 hour
        self.max_attempts_per_hour = 3  # Max 3 reset attempts per hour per user
    
    def generate_reset_code(self, length=6):
        """Generate a secure numeric reset code"""
        return ''.join(secrets.choice(string.digits) for _ in range(length))
    
    def send_email_reset(self, user, request):
        """Send password reset email"""
        try:
            # Generate secure token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL
            current_site = get_current_site(request)
            reset_url = f"http://{current_site.domain}/accounts/reset/{uid}/{token}/"
            
            # Email content
            subject = 'EcoLearn - Password Reset Request'
            message = render_to_string('accounts/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'EcoLearn',
                'expiry_hours': self.token_expiry_hours,
            })
            
            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=message,
                fail_silently=False
            )
            
            return {'success': True, 'method': 'email'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_sms_reset(self, user):
        """Send password reset SMS using Twilio"""
        try:
            from twilio.rest import Client
            
            # Generate 6-digit code
            reset_code = self.generate_reset_code()
            
            # Store code in user session or cache (you'll need to handle this)
            # For now, we'll store it in a custom field or use cache
            
            # Twilio setup
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            # SMS message
            message_body = f"""
EcoLearn Password Reset

Your reset code: {reset_code}

This code expires in {self.token_expiry_hours} hour(s).
If you didn't request this, ignore this message.

- EcoLearn Team
            """.strip()
            
            # Send SMS
            message = client.messages.create(
                body=message_body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=str(user.phone_number)
            )
            
            return {
                'success': True, 
                'method': 'sms',
                'code': reset_code,  # You'll store this securely
                'message_sid': message.sid
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_whatsapp_reset(self, user):
        """Send password reset via WhatsApp"""
        try:
            from twilio.rest import Client
            
            # Generate 6-digit code
            reset_code = self.generate_reset_code()
            
            # Twilio setup
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            # WhatsApp message
            message_body = f"""
🔐 *EcoLearn Password Reset*

Your reset code: *{reset_code}*

⏰ Expires in {self.token_expiry_hours} hour(s)
🚫 If you didn't request this, ignore this message

- EcoLearn Team 🌱
            """.strip()
            
            # Send WhatsApp
            message = client.messages.create(
                body=message_body,
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                to=f'whatsapp:{user.phone_number}'
            )
            
            return {
                'success': True,
                'method': 'whatsapp', 
                'code': reset_code,
                'message_sid': message.sid
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def validate_reset_token(self, uid, token):
        """Validate email-based reset token"""
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(pk=user_id)
            
            if default_token_generator.check_token(user, token):
                return {'valid': True, 'user': user}
            else:
                return {'valid': False, 'error': 'Invalid or expired token'}
                
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return {'valid': False, 'error': 'Invalid reset link'}
    
    def check_rate_limit(self, user):
        """Check if user has exceeded reset attempt rate limit"""
        # This is a simplified version - in production, use Redis or database
        # For now, we'll use a simple session-based approach
        return True  # Allow for now - implement proper rate limiting
    
    def reset_password(self, user, new_password):
        """Reset user password"""
        try:
            user.set_password(new_password)
            user.save()
            
            # Log the password reset
            print(f"Password reset successful for user: {user.username}")
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Global instance
password_reset_service = PasswordResetService()