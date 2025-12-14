from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
# from cloudinary.models import CloudinaryField  # Temporarily disabled

User = get_user_model()


class DumpingReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('verified', 'Verified'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    # Reporter information (anonymous option)
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_anonymous = models.BooleanField(default=True)
    reporter_contact = models.CharField(max_length=100, blank=True)  # Optional contact for follow-up
    
    # Location information
    location_description = models.CharField(max_length=500)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.CharField(max_length=500, blank=True)
    
    # Report details
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    waste_type = models.CharField(max_length=200, blank=True)  # e.g., "plastic bottles, food waste"
    estimated_volume = models.CharField(max_length=100, blank=True)  # e.g., "1-2 cubic meters"
    
    # Media files with Cloudinary optimization
    photo1 = models.ImageField(upload_to='images/', blank=True, null=True)
    photo2 = models.ImageField(upload_to='images/', blank=True, null=True)
    photo3 = models.ImageField(upload_to='images/', blank=True, null=True)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference_number = models.CharField(max_length=20, unique=True)
    
    # Authority information
    forwarded_to_authority = models.BooleanField(default=False)
    authority_name = models.CharField(max_length=200, blank=True)
    authority_contact = models.CharField(max_length=200, blank=True)
    authority_response = models.TextField(blank=True)
    
    # Timestamps
    reported_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Admin notes
    admin_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-reported_at']

    def __str__(self):
        return f"Report {self.reference_number} - {self.location_description}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Generate unique reference number
            import uuid
            self.reference_number = f"ECO{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)


class ReportUpdate(models.Model):
    report = models.ForeignKey(DumpingReport, on_delete=models.CASCADE, related_name='updates')
    update_text = models.TextField()
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)  # Whether visible to reporter
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Update for {self.report.reference_number}"


class Authority(models.Model):
    name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    api_endpoint = models.URLField(blank=True)  # For automated forwarding
    api_key = models.CharField(max_length=200, blank=True)
    coverage_areas = models.TextField(help_text="Comma-separated list of areas covered")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Authorities"

    def __str__(self):
        return self.name


class ReportStatistics(models.Model):
    """Model to track reporting statistics"""
    date = models.DateField(unique=True)
    total_reports = models.IntegerField(default=0)
    pending_reports = models.IntegerField(default=0)
    resolved_reports = models.IntegerField(default=0)
    average_resolution_days = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Statistics for {self.date}"
