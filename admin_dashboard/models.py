from django.db import models
from django.utils import timezone
# Create your models here.
# admin_dashboard/models.py
# Optional models for advanced analytics (e.g., ROI logs, SMS campaigns)

class AdminLog(models.Model):
    action = models.CharField(max_length=255)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.action} at {self.timestamp}"

class ROITracker(models.Model):
    month = models.DateField()
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costs = models.DecimalField(max_digits=10, decimal_places=2, default=3400)  # From budget
    benefits = models.DecimalField(max_digits=10, decimal_places=2, default=8700)  # From CBA
    roi = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        self.roi = round(((self.revenue + self.benefits - self.costs) / self.costs * 100), 1) if self.costs else 0
        super().save(*args, **kwargs)