"""
Custom adapters for django-allauth to integrate with existing registration system
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import UserProfile


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for regular email registration
    """
    
    def save_user(self, request, user, form, commit=True):
        """
        Save user and create profile
        """
        user = super().save_user(request, user, form, commit=False)
        
        # Set user as inactive until email verification
        user.is_active = False
        
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.get_or_create(user=user)
        
        return user
    
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Send custom verification email
        """
        current_site = self.get_current_site(request)
        activate_url = self.get_email_confirmation_url(request, emailconfirmation)
        
        context = {
            'user': emailconfirmation.email_address.user,
            'activate_url': activate_url,
            'current_site': current_site,
            'key': emailconfirmation.key,
        }
        
        subject = 'Verify your EcoLearn account'
        message = render_to_string('accounts/verification_email.html', context)
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [emailconfirmation.email_address.email],
            html_message=message
        )


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social authentication (Google)
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Handle account linking if email already exists
        """
        # If user is already logged in, link the account
        if request.user.is_authenticated:
            return
        
        # Check if email already exists
        if sociallogin.is_existing:
            return
        
        # Try to connect to existing email
        try:
            email = sociallogin.account.extra_data.get('email')
            if email:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user = User.objects.get(email=email)
                    # Connect social account to existing user
                    sociallogin.connect(request, user)
                except User.DoesNotExist:
                    pass
        except:
            pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save user from social login
        """
        user = super().save_user(request, sociallogin, form)
        
        # Google accounts are pre-verified
        user.is_active = True
        user.is_verified = True
        user.save()
        
        # Create user profile if doesn't exist
        UserProfile.objects.get_or_create(user=user)
        
        # Send welcome email
        self.send_welcome_email(user)
        
        return user
    
    def send_welcome_email(self, user):
        """
        Send welcome email to new Google sign-up users
        """
        try:
            context = {
                'user': user,
                'login_url': settings.LOGIN_REDIRECT_URL,
            }
            
            subject = 'Welcome to EcoLearn!'
            message = render_to_string('accounts/welcome_email.html', context)
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=message,
                fail_silently=True
            )
        except Exception as e:
            print(f"Error sending welcome email: {e}")
