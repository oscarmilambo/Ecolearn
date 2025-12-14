from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
# from cloudinary.models import CloudinaryField  # Temporarily disabled

User = get_user_model()


class CleanupGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    community = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    coordinator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coordinated_groups')
    members = models.ManyToManyField(User, through='GroupMembership', related_name='cleanup_groups')
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    
    # Social Media Links (Limited to 3 platforms)
    facebook_url = models.URLField(blank=True, help_text="Facebook page or group URL")
    whatsapp_url = models.URLField(blank=True, help_text="WhatsApp group invite link")
    twitter_url = models.URLField(blank=True, help_text="Twitter/X profile URL")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        return self.members.count()
    
    @property
    def total_impact(self):
        """Calculate total impact of group activities"""
        return {
            'events': self.events.count(),
            'reports': sum(m.user.report_set.count() for m in self.membership.all()),
            'tons_collected': sum(e.waste_collected for e in self.events.all() if e.waste_collected),
        }
    
    @property
    def social_media_links(self):
        """Get available social media links with icons (Facebook, WhatsApp, X only)"""
        links = []
        social_platforms = [
            ('facebook_url', 'fab fa-facebook-f', 'Facebook', '#1877f2'),
            ('whatsapp_url', 'fab fa-whatsapp', 'WhatsApp', '#25d366'),
            ('twitter_url', 'fab fa-x-twitter', 'X (Twitter)', '#000000'),
        ]
        
        for field_name, icon, name, color in social_platforms:
            url = getattr(self, field_name)
            if url:
                links.append({
                    'url': url,
                    'icon': icon,
                    'name': name,
                    'color': color
                })
        
        return links


class GroupMembership(models.Model):
    ROLE_CHOICES = [
        ('coordinator', 'Coordinator'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
    ]
    
    group = models.ForeignKey(CleanupGroup, on_delete=models.CASCADE, related_name='membership')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['group', 'user']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.role})"


class GroupEvent(models.Model):
    EVENT_STATUS = [
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    group = models.ForeignKey(CleanupGroup, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    scheduled_date = models.DateTimeField()
    duration_hours = models.IntegerField(default=2)
    status = models.CharField(max_length=20, choices=EVENT_STATUS, default='planned')
    waste_collected = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="In kilograms")
    participants_count = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"{self.group.name} - {self.title}"


class GroupChat(models.Model):
    group = models.ForeignKey(CleanupGroup, on_delete=models.CASCADE, related_name='chats')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    is_announcement = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username} in {self.group.name}"


class GroupImpactReport(models.Model):
    group = models.ForeignKey(CleanupGroup, on_delete=models.CASCADE, related_name='impact_reports')
    report_period_start = models.DateField()
    report_period_end = models.DateField()
    total_events = models.IntegerField(default=0)
    total_participants = models.IntegerField(default=0)
    waste_collected_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dumps_cleaned = models.IntegerField(default=0)
    reports_submitted = models.IntegerField(default=0)
    community_reach = models.IntegerField(default=0, help_text="Number of people reached")
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.group.name} - {self.report_period_start} to {self.report_period_end}"


class Badge(models.Model):
    BADGE_CATEGORIES = [
        ('learning', 'Learning Achievement'),
        ('reporting', 'Reporting Champion'),
        ('community', 'Community Leader'),
        ('impact', 'Environmental Impact'),
        ('special', 'Special Recognition'),
    ]
    
    name = models.CharField(max_length=100)
    name_bem = models.CharField(max_length=100, blank=True)
    name_ny = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=BADGE_CATEGORIES)
    icon = models.CharField(max_length=50, default='🏆')
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    points_required = models.IntegerField(default=0)
    criteria = models.TextField(help_text="Criteria to earn this badge")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class Leaderboard(models.Model):
    LEADERBOARD_TYPES = [
        ('individual', 'Individual'),
        ('community', 'Community'),
        ('district', 'District'),
    ]
    
    PERIOD_TYPES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('all_time', 'All Time'),
    ]
    
    leaderboard_type = models.CharField(max_length=20, choices=LEADERBOARD_TYPES)
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()
    data = models.JSONField(default=dict, help_text="Leaderboard rankings data")
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.get_leaderboard_type_display()} - {self.get_period_type_display()}"
