"""
Custom adapters for django-allauth - Phone number only authentication
"""
from allauth.account.adapter import DefaultAccountAdapter
from .models import UserProfile


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for phone number only registration
    """
    
    def save_user(self, request, user, form, commit=True):
        """
        Save user and create profile - no email verification needed
        """
        user = super().save_user(request, user, form, commit=False)
        
        # Set user as active immediately (no email verification)
        user.is_active = True
        
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.get_or_create(user=user)
        
        return user



