from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Sum
from cloudinary.models import CloudinaryField

User = get_user_model()


class PointTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('module_complete', 'Module Completed'),
        ('quiz_pass', 'Quiz Passed'),
        ('report_submit', 'Report Submitted'),
        ('event_attend', 'Event Attended'),
        ('story_share', 'Story Shared'),
        ('forum_post', 'Forum Post'),
        ('daily_login', 'Daily Login'),
        ('challenge_complete', 'Challenge Completed'),
        ('redemption', 'Points Redeemed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    points = models.IntegerField()
    description = models.CharField(max_length=255)
    reference_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.points} points - {self.transaction_type}"


class UserPoints(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_points')
    total_points = models.IntegerField(default=0)
    available_points = models.IntegerField(default=0)
    redeemed_points = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User Points"
    
    def __str__(self):
        return f"{self.user.username} - {self.total_points} points"
    
    def add_points(self, points, transaction_type, description, reference_id=None):
        self.total_points += points
        self.available_points += points
        self.save()
        
        # Create transaction record
        PointTransaction.objects.create(
            user=self.user,
            transaction_type=transaction_type,
            points=points,
            description=description,
            reference_id=reference_id
        )
        
        # REAL-TIME NOTIFICATION: Points awarded
        try:
            from community.notifications import notification_service
            from community.models import Notification
            
            # Notify user
            prefs = getattr(self.user, 'notification_preferences', None)
            
            # SMS to user
            if prefs and prefs.sms_enabled and self.user.phone_number:
                sms_message = f"🎉 +{points} points earned! {description}. Total: {self.total_points} points"
                notification_service.send_sms(str(self.user.phone_number), sms_message)
            
            # WhatsApp to user
            if prefs and prefs.whatsapp_enabled and self.user.phone_number:
                whatsapp_message = f"🎉 *Points Earned!*\n\n*+{points} points*\n\n{description}\n\n*Total Points:* {self.total_points}\n*Available:* {self.available_points}"
                notification_service.send_whatsapp(str(self.user.phone_number), whatsapp_message)
            
            # In-app notification to user
            Notification.objects.create(
                user=self.user,
                notification_type='achievement',
                title=f'+{points} Points Earned!',
                message=description,
                url='/gamification/leaderboard/'
            )
            
            # Log for admin view (create admin notification for significant points)
            if points >= 100:  # Only notify admins for significant point awards
                from accounts.models import CustomUser
                from django.db.models import Q
                
                admins = CustomUser.objects.filter(Q(is_superuser=True) | Q(is_staff=True))
                for admin in admins:
                    try:
                        Notification.objects.create(
                            user=admin,
                            notification_type='general',
                            title=f'Points Awarded: {self.user.username}',
                            message=f'{self.user.username} earned {points} points: {description}',
                            url=f'/admin-dashboard/users/{self.user.id}/'
                        )
                    except Exception as e:
                        print(f"Error creating admin notification: {e}")
        except Exception as e:
            print(f"Error in points notification: {e}")
    
    def redeem_points(self, points, description):
        if self.available_points >= points:
            self.available_points -= points
            self.redeemed_points += points
            self.save()
            
            PointTransaction.objects.create(
                user=self.user,
                transaction_type='redemption',
                points=-points,
                description=description
            )
            return True
        return False


class Challenge(models.Model):
    CHALLENGE_TYPES = [
        ('individual', 'Individual Challenge'),
        ('community', 'Community Challenge'),
        ('district', 'District Challenge'),
    ]
    
    title = models.CharField(max_length=200)
    title_bem = models.CharField(max_length=200, blank=True)
    title_ny = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    description_bem = models.TextField(blank=True)
    description_ny = models.TextField(blank=True)
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    points_reward = models.IntegerField(default=50)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    target_metric = models.CharField(max_length=100)  # e.g., "reports_submitted", "modules_completed"
    target_value = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date


class ChallengeParticipant(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gamification_challenges')
    progress = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['challenge', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"


class Reward(models.Model):
    REWARD_TYPES = [
        ('airtime', 'Airtime Voucher'),
        ('certificate', 'Recognition Certificate'),
        ('badge', 'Digital Badge'),
        ('merchandise', 'Eco Merchandise'),
    ]
    
    name = models.CharField(max_length=200)
    name_bem = models.CharField(max_length=200, blank=True)
    name_ny = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    points_cost = models.IntegerField()
    image = CloudinaryField('image', blank=True,
                           transformation={'width': 400, 'height': 300, 'crop': 'fill', 'format': 'webp', 'quality': 'auto'})
    stock_quantity = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.points_cost} points"


class RewardRedemption(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='redemptions')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    points_spent = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    redemption_code = models.CharField(max_length=50, unique=True)
    contact_info = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    redeemed_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-redeemed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.reward.name}"
    
    def save(self, *args, **kwargs):
        if not self.redemption_code:
            import uuid
            self.redemption_code = f"RWD{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)


class CommunityImpact(models.Model):
    community_name = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    total_reports = models.IntegerField(default=0)
    resolved_reports = models.IntegerField(default=0)
    tons_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dumps_cleaned = models.IntegerField(default=0)
    active_members = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Community Impact Metrics"
    
    def __str__(self):
        return f"{self.community_name} - {self.district}"
