from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.contrib.contenttypes.fields import GenericRelation
from cloudinary.models import CloudinaryField

User = get_user_model()


# ====================== FORUM SYSTEM ======================
class ForumCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category Name (English)")
    name_bem = models.CharField(max_length=100, blank=True, verbose_name="Name (Bemba)")
    name_ny = models.CharField(max_length=100, blank=True, verbose_name="Name (Nyanja)")
    
    description = models.TextField(verbose_name="Description (English)")
    description_bem = models.TextField(blank=True, verbose_name="Description (Bemba)")
    description_ny = models.TextField(blank=True, verbose_name="Description (Nyanja)")
    
    icon = models.CharField(max_length=50, default="comments", help_text="FontAwesome class e.g. fa-comments")
    order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Forum Categories"
        ordering = ['order', 'name']
        indexes = [models.Index(fields=['order'])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('community:category_topics', args=[self.id])


class ForumTopic(models.Model):
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics')
    content = models.TextField()
    is_pinned = models.BooleanField(default=False, verbose_name="Pin to top")
    is_locked = models.BooleanField(default=False, verbose_name="Lock topic (no new replies)")
    views = models.PositiveIntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-updated_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['-is_pinned', '-updated_at']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('community:topic_detail', args=[self.id])

    @property
    def reply_count(self):
        return self.replies.count()

    @property
    def last_reply(self):
        return self.replies.order_by('-created_at').first()


class ForumReply(models.Model):
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_replies')
    content = models.TextField()
    is_solution = models.BooleanField(default=False, help_text="Mark as accepted solution")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [models.Index(fields=['-created_at'])]

    def __str__(self):
        return f"Reply by {self.author.get_full_name() or self.author.username}"


# ====================== COMMUNITY EVENTS ======================
class CommunityEvent(models.Model):
    EVENT_TYPES = [
        ('cleanup', 'Community Cleanup'),
        ('workshop', 'Educational Workshop'),
        ('campaign', 'Awareness Campaign'),
        ('competition', 'Eco Competition'),
    ]

    title = models.CharField(max_length=200)
    title_bem = models.CharField(max_length=200, blank=True)
    title_ny = models.CharField(max_length=200, blank=True)
    
    description = models.TextField()
    description_bem = models.TextField(blank=True)
    description_ny = models.TextField(blank=True)
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='cleanup')
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    image = CloudinaryField('image', blank=True, null=True,
                           transformation={'width': 800, 'height': 600, 'crop': 'fill', 'format': 'webp', 'quality': 'auto'})
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Generic relation for participants
    participants = GenericRelation('EventParticipant', related_query_name='event')

    class Meta:
        ordering = ['-start_date']
        indexes = [models.Index(fields=['start_date'])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('community:event_detail', args=[self.id])

    @property
    def participant_count(self):
        return self.participants.count()

    @property
    def is_full(self):
        return self.max_participants and self.participant_count >= self.max_participants

    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()

    @property
    def is_ongoing(self):
        return self.start_date <= timezone.now() <= self.end_date

    @property
    def is_past(self):
        return self.end_date < timezone.now()


class EventParticipant(models.Model):
    event = models.ForeignKey(CommunityEvent, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False, help_text="Did the user attend?")

    class Meta:
        unique_together = ['event', 'user']
        indexes = [models.Index(fields=['event', 'user'])]

    def __str__(self):
        return f"{self.user} → {self.event}"


# ====================== SUCCESS STORIES ======================
class SuccessStory(models.Model):
    STORY_TYPES = [
        ('recycling', 'Recycling Success'),
        ('cleanup', 'Community Cleanup'),
        ('education', 'Environmental Education'),
        ('innovation', 'Eco Innovation'),
    ]

    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='success_stories')
    story_type = models.CharField(max_length=20, choices=STORY_TYPES)
    content = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    image = CloudinaryField('image', blank=True, null=True,
                           transformation={'width': 800, 'height': 600, 'crop': 'fill', 'format': 'webp', 'quality': 'auto'})
    video_url = models.URLField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False, help_text="Requires admin approval")
    likes = models.ManyToManyField(User, related_name='liked_stories', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name_plural = "Success Stories"
        indexes = [models.Index(fields=['-created_at'])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('community:story_detail', args=[self.id])

    @property
    def like_count(self):
        return self.likes.count()


# ====================== SOCIAL SHARING TRACKING ======================
class SocialMediaShare(models.Model):
    PLATFORM_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('copy', 'Copy Link'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    content_type = models.CharField(max_length=50)  # e.g., 'success_story', 'event'
    content_id = models.PositiveIntegerField()
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['-shared_at'])]

    def __str__(self):
        return f"{self.user} shared {self.content_type} on {self.get_platform_display()}"


# ====================== NOTIFICATIONS ======================
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('event_reminder', 'Event Reminder'),
        ('new_event', 'New Event'),
        ('forum_reply', 'Forum Reply'),
        ('story_approved', 'Story Approved'),
        ('achievement', 'Achievement Unlocked'),
        ('health_alert', 'Health Alert'),
        ('emergency', 'Emergency Alert'),
        ('challenge_update', 'Challenge Update'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    url = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    is_sent_sms = models.BooleanField(default=False)
    is_sent_whatsapp = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['-created_at', 'is_read'])]

    def __str__(self):
        return f"{self.user} - {self.title}"


# ====================== HEALTH ALERTS ======================
class HealthAlert(models.Model):
    ALERT_TYPES = [
        ('cholera', 'Cholera Outbreak'),
        ('flooding', 'Flooding'),
        ('hazardous_waste', 'Hazardous Waste'),
        ('water_contamination', 'Water Contamination'),
        ('air_pollution', 'Air Pollution'),
        ('disease', 'Disease Outbreak'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='medium')
    title = models.CharField(max_length=200)
    message = models.TextField()
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    affected_areas = models.TextField(help_text="Comma-separated list")
    hygiene_tips = models.TextField()
    nearest_clinics = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_alerts')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-severity', '-created_at']
        indexes = [models.Index(fields=['is_active', '-created_at'])]

    def __str__(self):
        return f"[{self.get_severity_display()}] {self.title}"


# ====================== COMMUNITY CAMPAIGNS ======================
class CommunityCampaign(models.Model):
    """
    Periodic waste management campaigns (FR08)
    """
    RECURRENCE_CHOICES = [
        ('one_time', 'One-time Event'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    CAMPAIGN_TYPES = [
        ('cleanup', 'Community Cleanup'),
        ('workshop', 'Segregation Workshop'),
        ('challenge', 'Zero-Plastic Challenge'),
        ('education', 'Waste Management Education'),
        ('recycling', 'Recycling Drive'),
        ('composting', 'Composting Workshop'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Campaign Title")
    title_bem = models.CharField(max_length=200, blank=True, verbose_name="Title (Bemba)")
    title_ny = models.CharField(max_length=200, blank=True, verbose_name="Title (Nyanja)")
    
    description = models.TextField(verbose_name="Campaign Description")
    description_bem = models.TextField(blank=True, verbose_name="Description (Bemba)")
    description_ny = models.TextField(blank=True, verbose_name="Description (Nyanja)")
    
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES, default='cleanup')
    location = models.CharField(max_length=255, verbose_name="Campaign Location")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    start_date = models.DateTimeField(verbose_name="Start Date & Time")
    end_date = models.DateTimeField(verbose_name="End Date & Time")
    
    # Recurrence settings
    recurrence = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='one_time')
    next_occurrence = models.DateTimeField(null=True, blank=True, help_text="Auto-calculated next occurrence")
    
    # Registration settings
    max_participants = models.PositiveIntegerField(null=True, blank=True, verbose_name="Maximum Participants")
    registration_deadline = models.DateTimeField(null=True, blank=True)
    
    # Campaign details
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_campaigns')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Contact Phone")
    contact_email = models.EmailField(blank=True, verbose_name="Contact Email")
    
    # Media
    image = CloudinaryField('image', blank=True, null=True,
                           transformation={'width': 1200, 'height': 400, 'crop': 'fill', 'format': 'webp', 'quality': 'auto'})
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Active Campaign")
    is_published = models.BooleanField(default=False, verbose_name="Published (visible to users)")
    
    # Tracking
    participant_count = models.PositiveIntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Community Campaign"
        verbose_name_plural = "Community Campaigns"
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['is_active', 'is_published']),
        ]

    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%B %d, %Y')}"

    def get_absolute_url(self):
        return reverse('community:campaign_detail', args=[self.id])

    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()

    @property
    def is_ongoing(self):
        return self.start_date <= timezone.now() <= self.end_date

    @property
    def is_past(self):
        return self.end_date < timezone.now()

    @property
    def is_full(self):
        return self.max_participants and self.participant_count >= self.max_participants

    @property
    def can_register(self):
        """Check if users can still register"""
        if not self.is_active or not self.is_published:
            return False
        if self.is_full:
            return False
        if self.registration_deadline and timezone.now() > self.registration_deadline:
            return False
        if self.is_past:
            return False
        return True

    def create_next_occurrence(self):
        """Create next occurrence for recurring campaigns"""
        if self.recurrence == 'one_time':
            return None
        
        from dateutil.relativedelta import relativedelta
        
        if self.recurrence == 'monthly':
            next_start = self.start_date + relativedelta(months=1)
            next_end = self.end_date + relativedelta(months=1)
        elif self.recurrence == 'quarterly':
            next_start = self.start_date + relativedelta(months=3)
            next_end = self.end_date + relativedelta(months=3)
        elif self.recurrence == 'yearly':
            next_start = self.start_date + relativedelta(years=1)
            next_end = self.end_date + relativedelta(years=1)
        else:
            return None
        
        # Create new campaign instance
        new_campaign = CommunityCampaign.objects.create(
            title=self.title,
            title_bem=self.title_bem,
            title_ny=self.title_ny,
            description=self.description,
            description_bem=self.description_bem,
            description_ny=self.description_ny,
            campaign_type=self.campaign_type,
            location=self.location,
            latitude=self.latitude,
            longitude=self.longitude,
            start_date=next_start,
            end_date=next_end,
            recurrence=self.recurrence,
            max_participants=self.max_participants,
            registration_deadline=next_start - timezone.timedelta(days=1) if self.registration_deadline else None,
            organizer=self.organizer,
            contact_phone=self.contact_phone,
            contact_email=self.contact_email,
            image=self.image,
            is_active=True,
            is_published=True,
        )
        
        # Update next occurrence
        self.next_occurrence = next_start
        self.save(update_fields=['next_occurrence'])
        
        return new_campaign


class CampaignParticipant(models.Model):
    """
    Track campaign participants and send reminders (FR09)
    """
    campaign = models.ForeignKey(CommunityCampaign, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campaign_participations')
    
    # Registration details
    registered_at = models.DateTimeField(auto_now_add=True)
    interest_level = models.CharField(
        max_length=20,
        choices=[
            ('join', 'Will Join'),
            ('interested', 'Interested'),
            ('maybe', 'Maybe'),
        ],
        default='join'
    )
    
    # Attendance tracking
    attended = models.BooleanField(default=False, help_text="Did the user attend?")
    attendance_confirmed_at = models.DateTimeField(null=True, blank=True)
    
    # Reminder tracking (FR09)
    reminder_3days_sent = models.BooleanField(default=False)
    reminder_1day_sent = models.BooleanField(default=False)
    confirmation_sent = models.BooleanField(default=False)

    class Meta:
        unique_together = ['campaign', 'user']
        verbose_name = "Campaign Participant"
        verbose_name_plural = "Campaign Participants"
        indexes = [
            models.Index(fields=['campaign', 'user']),
            models.Index(fields=['registered_at']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} → {self.campaign.title}"

    def send_confirmation(self):
        """Send registration confirmation"""
        if self.confirmation_sent:
            return
        
        try:
            from .notifications import notification_service
            
            user_name = self.user.get_full_name() or self.user.username
            prefs = getattr(self.user, 'notification_preferences', None)
            
            # SMS confirmation
            if prefs and prefs.sms_enabled and prefs.event_reminders and self.user.phone_number:
                sms_message = f"✅ {user_name}, you're registered for {self.campaign.title} on {self.campaign.start_date.strftime('%B %d, %Y at %I:%M %p')}. Location: {self.campaign.location}"
                result = notification_service.send_sms(str(self.user.phone_number), sms_message)
                if result.get('success'):
                    print(f"✅ Campaign confirmation SMS sent to {self.user.username}")
            
            # WhatsApp confirmation
            if prefs and prefs.whatsapp_enabled and prefs.event_reminders and self.user.phone_number:
                whatsapp_message = f"✅ *Campaign Registration Confirmed*\n\n*Campaign:* {self.campaign.title}\n*Date:* {self.campaign.start_date.strftime('%B %d, %Y at %I:%M %p')}\n*Location:* {self.campaign.location}\n\nThank you for joining our waste management initiative!"
                result = notification_service.send_whatsapp(str(self.user.phone_number), whatsapp_message)
                if result.get('success'):
                    print(f"✅ Campaign confirmation WhatsApp sent to {self.user.username}")
            
            # In-app notification
            Notification.objects.create(
                user=self.user,
                notification_type='event_reminder',
                title=f'Registered for {self.campaign.title}',
                message=f'You have successfully registered for {self.campaign.title} on {self.campaign.start_date.strftime("%B %d, %Y")}.',
                url=self.campaign.get_absolute_url()
            )
            
            self.confirmation_sent = True
            self.save(update_fields=['confirmation_sent'])
            
        except Exception as e:
            print(f"Campaign confirmation error: {e}")

    def send_reminder(self, days_before):
        """Send campaign reminder (3 days or 1 day before)"""
        try:
            from .notifications import notification_service
            
            user_name = self.user.get_full_name() or self.user.username
            prefs = getattr(self.user, 'notification_preferences', None)
            
            if days_before == 3:
                if self.reminder_3days_sent:
                    return
                reminder_text = "in 3 days"
                field_to_update = 'reminder_3days_sent'
            elif days_before == 1:
                if self.reminder_1day_sent:
                    return
                reminder_text = "tomorrow"
                field_to_update = 'reminder_1day_sent'
            else:
                return
            
            # SMS reminder
            if prefs and prefs.sms_enabled and prefs.event_reminders and self.user.phone_number:
                sms_message = f"⏰ Reminder: {self.campaign.title} is {reminder_text} at {self.campaign.start_date.strftime('%I:%M %p')}. Location: {self.campaign.location}. See you there!"
                result = notification_service.send_sms(str(self.user.phone_number), sms_message)
                if result.get('success'):
                    print(f"✅ Campaign {days_before}-day reminder SMS sent to {self.user.username}")
            
            # WhatsApp reminder
            if prefs and prefs.whatsapp_enabled and prefs.event_reminders and self.user.phone_number:
                whatsapp_message = f"⏰ *Campaign Reminder*\n\n*{self.campaign.title}* is {reminder_text}!\n\n*Time:* {self.campaign.start_date.strftime('%I:%M %p')}\n*Location:* {self.campaign.location}\n\nDon't forget to bring gloves and water. See you there! 🌍"
                result = notification_service.send_whatsapp(str(self.user.phone_number), whatsapp_message)
                if result.get('success'):
                    print(f"✅ Campaign {days_before}-day reminder WhatsApp sent to {self.user.username}")
            
            # In-app notification
            Notification.objects.create(
                user=self.user,
                notification_type='event_reminder',
                title=f'Reminder: {self.campaign.title}',
                message=f'Your registered campaign {self.campaign.title} is {reminder_text}!',
                url=self.campaign.get_absolute_url()
            )
            
            # Update reminder status
            setattr(self, field_to_update, True)
            self.save(update_fields=[field_to_update])
            
        except Exception as e:
            print(f"Campaign reminder error: {e}")


# ====================== COMMUNITY CHALLENGES ======================
class CommunityChallenge(models.Model):
    CHALLENGE_TYPES = [
        ('cleanup', 'Cleanup Challenge'),
        ('recycling', 'Recycling Challenge'),
        ('education', 'Education Challenge'),
        ('reporting', 'Reporting Challenge'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    target_goal = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    current_progress = models.PositiveIntegerField(default=0)
    reward_points = models.PositiveIntegerField(default=100)
    image = CloudinaryField('image', blank=True, null=True,
                           transformation={'width': 800, 'height': 600, 'crop': 'fill', 'format': 'webp', 'quality': 'auto'})
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        indexes = [models.Index(fields=['is_active', 'end_date'])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('community:challenge_detail', args=[self.id])

    @property
    def progress_percentage(self):
        if self.target_goal <= 0:
            return 0
        return min(100, int((self.current_progress / self.target_goal) * 100))

    @property
    def is_completed(self):
        return self.current_progress >= self.target_goal

    @property
    def is_active_challenge(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date


class ChallengeParticipant(models.Model):
    challenge = models.ForeignKey(CommunityChallenge, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenge_participations')
    contribution = models.PositiveIntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['challenge', 'user']
        ordering = ['-contribution']
        indexes = [models.Index(fields=['challenge', '-contribution'])]

    def __str__(self):
        return f"{self.user} in {self.challenge}"


class ChallengeProof(models.Model):
    """Proof submission for challenge participation"""
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    participant = models.ForeignKey(ChallengeParticipant, on_delete=models.CASCADE, related_name='proofs')
    before_photo = CloudinaryField('image', help_text='Required: Before photo',
                                  transformation={'width': 600, 'height': 450, 'crop': 'fill', 'format': 'webp', 'quality': 'auto'})
    after_photo = CloudinaryField('image', blank=True, null=True, help_text='Optional: After photo',
                                 transformation={'width': 600, 'height': 450, 'crop': 'fill', 'format': 'webp', 'quality': 'auto'})
    bags_collected = models.PositiveIntegerField(default=0, help_text='Number of bags collected')
    description = models.TextField(blank=True, help_text='Optional description')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    points_awarded = models.PositiveIntegerField(default=0, editable=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_proofs')
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-submitted_at']
        indexes = [models.Index(fields=['status', '-submitted_at'])]

    def __str__(self):
        return f"Proof by {self.participant.user} - {self.get_status_display()}"
    
    def approve(self, admin_user):
        """Approve proof and award points"""
        if self.status == 'approved':
            return
        
        self.status = 'approved'
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        
        # Award 30 points per bag
        points = self.bags_collected * 30
        self.points_awarded = points
        
        # Update participant contribution
        self.participant.contribution += self.bags_collected
        self.participant.save()
        
        # Update challenge progress
        self.participant.challenge.current_progress += self.bags_collected
        self.participant.challenge.save()
        
        # Award points to user in gamification system
        try:
            from gamification.models import UserPoints
            user_points, created = UserPoints.objects.get_or_create(user=self.participant.user)
            user_points.add_points(points, 'challenge_complete', f'Challenge proof approved: {self.bags_collected} bags', reference_id=self.id)
        except Exception as e:
            print(f"Gamification points error: {e}")
        
        # Award points to user profile (main points display)
        try:
            from accounts.models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=self.participant.user)
            profile.points += points
            profile.save()
        except Exception as e:
            print(f"UserProfile points error: {e}")
        
        self.save()
    
    def reject(self, admin_user, reason=''):
        """Reject proof submission"""
        self.status = 'rejected'
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.admin_notes = reason
        self.save()


class SocialShare(models.Model):
    """
    Track social media shares for analytics
    """
    from django.contrib.contenttypes.fields import GenericForeignKey
    from django.contrib.contenttypes.models import ContentType
    
    user = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='social_shares'
    )
    
    # Generic relation to any shareable content
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    PLATFORM_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn'),
        ('email', 'Email'),
    ]
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES
    )
    
    shared_at = models.DateTimeField(auto_now_add=True)
    clicks = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Social Share'
        verbose_name_plural = 'Social Shares'
        ordering = ['-shared_at']
    
    def __str__(self):
        return f"{self.user.username} shared via {self.platform}"


class NotificationLog(models.Model):
    """
    Log all notifications sent for tracking and debugging
    """
    user = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='notification_logs'
    )
    
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
    ]
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    
    notification_type = models.CharField(max_length=50)
    message = models.TextField()
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # External service IDs
    message_sid = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Notification Log'
        verbose_name_plural = 'Notification Logs'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.channel} to {self.user.username} - {self.status}"
