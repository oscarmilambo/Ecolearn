from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from cloudinary.models import CloudinaryField


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
    profile_picture = CloudinaryField(
        'image', 
        blank=True, null=True,
        verbose_name=_('Profile Picture'),
        transformation={'width': 200, 'height': 200, 'crop': 'fill', 'format': 'webp', 'quality': 'auto'}
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
    
    # User Role Management
    USER_ROLES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Administrator'),
        ('moderator', 'Moderator'),
        ('super_admin', 'Super Administrator'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('bem', 'Bemba'),
        ('ny', 'Nyanja'),
    ]
    
    # Role and permissions
    role = models.CharField(max_length=20, choices=USER_ROLES, default='student')
    
    # Contact and profile information
    phone_number = PhoneNumberField(blank=True, null=True, unique=True)
    preferred_language = models.CharField(
        max_length=3, 
        choices=LANGUAGE_CHOICES, 
        default='en'
    )
    profile_picture = CloudinaryField(
        'image', 
        blank=True, null=True,
        transformation={'width': 200, 'height': 200, 'crop': 'fill', 'format': 'webp', 'quality': 'auto'}
    )
    date_of_birth = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    
    # Verification and security
    is_verified = models.BooleanField(default=False)
    sms_verification_code = models.CharField(max_length=6, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username or str(self.phone_number)
    
    # Role-based permission methods
    def is_student(self):
        """Check if user is a student"""
        return self.role == 'student'
    
    def is_instructor(self):
        """Check if user is an instructor"""
        return self.role == 'instructor'
    
    def is_admin_user(self):
        """Check if user has admin privileges"""
        return self.role in ['admin', 'moderator', 'super_admin'] or self.is_staff or self.is_superuser
    
    def is_moderator(self):
        """Check if user is a moderator"""
        return self.role == 'moderator'
    
    def is_super_admin(self):
        """Check if user is a super admin"""
        return self.role == 'super_admin' or self.is_superuser
    
    def can_access_admin_dashboard(self):
        """Check if user can access admin dashboard"""
        return self.is_admin_user()
    
    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.role in ['admin', 'super_admin'] or self.is_superuser
    
    def can_manage_content(self):
        """Check if user can manage learning content"""
        return self.role in ['instructor', 'admin', 'super_admin'] or self.is_staff
    
    def can_moderate_reports(self):
        """Check if user can moderate dumping reports"""
        return self.role in ['moderator', 'admin', 'super_admin'] or self.is_staff
    
    def get_role_display_with_icon(self):
        """Get role display with appropriate icon"""
        role_icons = {
            'student': '🎓',
            'instructor': '👨‍🏫',
            'admin': '👨‍💼',
            'moderator': '🛡️',
            'super_admin': '👑',
        }
        icon = role_icons.get(self.role, '👤')
        return f"{icon} {self.get_role_display()}"
    
    def get_dashboard_url(self):
        """Get appropriate dashboard URL based on role"""
        if self.can_access_admin_dashboard():
            return 'admin_dashboard:dashboard'
        else:
            return 'dashboard'


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
