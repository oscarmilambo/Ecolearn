from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
import secrets
import string
from datetime import timedelta

# Note: Using ImageField for now, can be upgraded to CloudinaryField later


class CustomUser(AbstractUser):
    # === USERNAME: NO RESTRICTIONS + FULLY CUSTOMIZABLE ===
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text=_('Enter any username you like - no character restrictions'),
        validators=[],  # ← REMOVED ALL DEFAULT VALIDATORS
        error_messages={
            'unique': _("This username is already taken. Please choose another."),
        },
    )

    # === ROLE FIELD: REQUIRED FOR ADMIN TOGGLE & ACCESS CONTROL ===
    ROLE_CHOICES = [
        ('user', _('User')),
        ('admin', _('Admin')),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name=_('User Role'),
        help_text=_('Controls access to admin features and dashboard switching')
    )

    # === PREFERRED LANGUAGE: SUPPORTS MULTILINGUAL ===
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('bem', 'Chibemba'),
        ('ny', 'Chinyanja'),
    ]
    preferred_language = models.CharField(
        max_length=3,
        choices=LANGUAGE_CHOICES,
        default='en',
        verbose_name=_('Preferred Language')
    )

    # === PROFILE FIELDS (Optional but recommended) ===
    GENDER_CHOICES = [
        ('female', 'Female'),
        ('male', 'Male'),
        ('custom', 'Custom'),
    ]
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True, null=True,
        verbose_name=_('Gender')
    )
    
    phone_number = models.CharField(
        max_length=15,
        blank=True, null=True,
        verbose_name=_('Phone Number')
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_('Bio')
    )
    # Profile picture field - fallback to ImageField if Cloudinary not available
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name=_('Profile Picture')
    )
    
    # Location field (from old migrations)
    location = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name=_('Location')
    )

    # === TIMESTAMPS ===
    date_joined = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    # === HELPER METHODS ===
    def is_admin(self):
        return self.role == 'admin'

    def __str__(self):
        return self.get_full_name() or self.username

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']


class PasswordResetAttempt(models.Model):
    """Track password reset attempts for rate limiting"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reset_attempts')
    ip_address = models.GenericIPAddressField()
    method = models.CharField(max_length=20)
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Password Reset Attempt'
        verbose_name_plural = 'Password Reset Attempts'


class UserProfile(models.Model):
    bio = models.TextField(max_length=500, blank=True)
    points = models.IntegerField(default=0)
    certificates_earned = models.IntegerField(default=0)
    modules_completed = models.IntegerField(default=0)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='userprofile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    preferred_language = models.CharField(max_length=10, choices=[('en','English'),('bem','Bemba'),('ny','Nyanja')], default='en')
    progress_percentage = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class PasswordResetCode(models.Model):
    """Model to store password reset codes"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)  # 10 minutes expiry
        super().save(*args, **kwargs)
    
    def generate_code(self):
        """Generate a 6-digit numeric code"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    def is_expired(self):
        """Check if the code has expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if the code is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Password Reset Code'
        verbose_name_plural = 'Password Reset Codes'
        
    def __str__(self):
        return f"Reset code for {self.user.username} - {self.code}"



class NotificationPreference(models.Model):
    """
    User notification preferences for SMS, WhatsApp, and Email
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Channel Preferences
    sms_enabled = models.BooleanField(
        default=True,
        verbose_name='SMS Notifications',
        help_text='Receive SMS notifications'
    )
    whatsapp_enabled = models.BooleanField(
        default=True,
        verbose_name='WhatsApp Notifications',
        help_text='Receive WhatsApp notifications'
    )
    email_enabled = models.BooleanField(
        default=True,
        verbose_name='Email Notifications',
        help_text='Receive email notifications'
    )
    
    # Notification Type Preferences
    event_reminders = models.BooleanField(
        default=True,
        verbose_name='Event Reminders',
        help_text='Get notified about upcoming events'
    )
    challenge_updates = models.BooleanField(
        default=True,
        verbose_name='Challenge Updates',
        help_text='Receive updates on your challenge progress'
    )
    forum_replies = models.BooleanField(
        default=True,
        verbose_name='Forum Replies',
        help_text='Get notified when someone replies to your posts'
    )
    reward_updates = models.BooleanField(
        default=True,
        verbose_name='Reward Updates',
        help_text='Receive updates on reward redemptions'
    )
    community_news = models.BooleanField(
        default=True,
        verbose_name='Community News',
        help_text='Get updates about community activities'
    )
    
    # Frequency
    FREQUENCY_CHOICES = [
        ('instant', 'Instant'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Summary'),
    ]
    frequency = models.CharField(
        max_length=10,
        choices=FREQUENCY_CHOICES,
        default='instant',
        verbose_name='Notification Frequency'
    )
    
    # Quiet Hours
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Quiet Hours Start',
        help_text='No notifications during quiet hours (e.g., 22:00)'
    )
    quiet_hours_end = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Quiet Hours End',
        help_text='Resume notifications after quiet hours (e.g., 07:00)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"{self.user.username}'s Notification Preferences"
    
    def is_quiet_hours(self):
        """Check if current time is within quiet hours"""
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        
        from django.utils import timezone
        now = timezone.localtime().time()
        
        if self.quiet_hours_start < self.quiet_hours_end:
            return self.quiet_hours_start <= now <= self.quiet_hours_end
        else:
            # Quiet hours span midnight
            return now >= self.quiet_hours_start or now <= self.quiet_hours_end
