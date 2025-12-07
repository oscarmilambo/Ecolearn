from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class PaymentProvider(models.Model):
    PROVIDER_CHOICES = [
        ('mtn', 'MTN Mobile Money'),
        ('airtel', 'Airtel Money'),
        ('zamtel', 'Zamtel Kwacha'),
    ]

    name = models.CharField(max_length=50, choices=PROVIDER_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    api_endpoint = models.URLField()
    api_key = models.CharField(max_length=200)
    api_secret = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    test_mode = models.BooleanField(default=True)
    
    def __str__(self):
        return self.display_name


class PaymentPlan(models.Model):
    PLAN_TYPES = [
        ('premium', 'Premium Access'),
        ('certificate', 'Certificate Fee'),
        ('donation', 'Community Donation'),
        ('event', 'Event Registration'),
    ]

    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ZMW')  # Zambian Kwacha
    duration_days = models.IntegerField(null=True, blank=True)  # For subscriptions
    features = models.JSONField(default=list)  # List of features
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.currency} {self.price}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    # Payment identification
    payment_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    transaction_id = models.CharField(max_length=100, blank=True)  # Provider transaction ID
    
    # User and plan information
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE)
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ZMW')
    provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50)  # e.g., "mtn_mobile_money"
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Provider response data
    provider_response = models.JSONField(default=dict)
    failure_reason = models.TextField(blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)  # Additional data like event_id, etc.

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.payment_id} - {self.user.username} - {self.currency} {self.amount}"

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = str(uuid.uuid4())[:12].upper()
        super().save(*args, **kwargs)


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'plan']

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

    @property
    def is_expired(self):
        return timezone.now() > self.end_date

    def save(self, *args, **kwargs):
        if not self.end_date and self.plan.duration_days:
            self.end_date = self.start_date + timezone.timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)


class PaymentWebhook(models.Model):
    provider = models.CharField(max_length=50)
    webhook_data = models.JSONField()
    processed = models.BooleanField(default=False)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Webhook from {self.provider} - {self.created_at}"


class PaymentStatistics(models.Model):
    date = models.DateField(unique=True)
    total_payments = models.IntegerField(default=0)
    successful_payments = models.IntegerField(default=0)
    failed_payments = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    mtn_payments = models.IntegerField(default=0)
    airtel_payments = models.IntegerField(default=0)
    zamtel_payments = models.IntegerField(default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Payment Stats for {self.date}"
