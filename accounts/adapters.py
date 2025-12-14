"""
Custom adapters for django-allauth email/password authentication
"""
from allauth.account.adapter import DefaultAccountAdapter
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



