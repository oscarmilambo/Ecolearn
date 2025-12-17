# Add this to your accounts/models.py file

import secrets
import string
from django.db import models
from django.utils import timezone
from datetime import timedelta

class PasswordResetCode(models.Model):
    """Model to store password reset codes"""
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
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
        
    def __str__(self):
        return f"Reset code for {self.user.username} - {self.code}"