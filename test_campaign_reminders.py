#!/usr/bin/env python
"""
Test campaign reminder system
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import get_user_model
from community.models import CommunityCampaign, CampaignParticipant
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

print("="*60)
print("TESTING CAMPAIGN REMINDER SYSTEM")
print("="*60)

# Get or create test user
try:
    user = User.objects.get(username='reminderuser')
    created = False
except User.DoesNotExist:
    user = User.objects.create_user(
        username='reminderuser',
        email='reminder@example.com',
        first_name='Reminder',
        last_name='User',
        phone_number='+260977654321'  # Unique Zambian number
    )
    created = True
if created:
    user.set_password('reminderpass123')
    user.save()
    print(f"✅ Created test user: {user.username}")
else:
    print(f"✅ Using existing user: {user.username}")

# Create test campaigns for different reminder scenarios
print("\n1. Creating test campaigns...")

# Campaign in 3 days
campaign_3days = CommunityCampaign.objects.create(
    title="Test Campaign - 3 Days",
    description="A test campaign starting in 3 days for reminder testing",
    campaign_type="cleanup",
    location="Test Location - 3 Days",
    start_date=timezone.now() + timedelta(days=3),
    end_date=timezone.now() + timedelta(days=3, hours=4),
    recurrence="one_time",
    organizer=user,  # Required field
    is_active=True,
    is_published=True
)

# Campaign in 1 day
campaign_1day = CommunityCampaign.objects.create(
    title="Test Campaign - 1 Day",
    description="A test campaign starting in 1 day for reminder testing",
    campaign_type="workshop",
    location="Test Location - 1 Day",
    start_date=timezone.now() + timedelta(days=1),
    end_date=timezone.now() + timedelta(days=1, hours=3),
    recurrence="one_time",
    organizer=user,  # Required field
    is_active=True,
    is_published=True
)

print(f"✅ Created campaign for 3-day reminder: {campaign_3days.title}")
print(f"✅ Created campaign for 1-day reminder: {campaign_1day.title}")

# Register user for campaigns
print("\n2. Registering user for campaigns...")

participant_3days, created = CampaignParticipant.objects.get_or_create(
    campaign=campaign_3days,
    user=user,
    defaults={'interest_level': 'join'}
)
if created:
    print(f"✅ Registered user for 3-day campaign")
else:
    print(f"ℹ️  User already registered for 3-day campaign")

participant_1day, created = CampaignParticipant.objects.get_or_create(
    campaign=campaign_1day,
    user=user,
    defaults={'interest_level': 'join'}
)
if created:
    print(f"✅ Registered user for 1-day campaign")
else:
    print(f"ℹ️  User already registered for 1-day campaign")

# Test reminder methods
print("\n3. Testing reminder methods...")

print(f"\nTesting 3-day reminder for: {campaign_3days.title}")
try:
    participant_3days.send_reminder(3)
    print("✅ 3-day reminder sent successfully")
except Exception as e:
    print(f"❌ 3-day reminder failed: {e}")

print(f"\nTesting 1-day reminder for: {campaign_1day.title}")
try:
    participant_1day.send_reminder(1)
    print("✅ 1-day reminder sent successfully")
except Exception as e:
    print(f"❌ 1-day reminder failed: {e}")

# Check reminder flags
print("\n4. Checking reminder flags...")
participant_3days.refresh_from_db()
participant_1day.refresh_from_db()

print(f"3-day campaign reminder flags:")
print(f"  - 3-day sent: {participant_3days.reminder_3days_sent}")
print(f"  - 1-day sent: {participant_3days.reminder_1day_sent}")

print(f"1-day campaign reminder flags:")
print(f"  - 3-day sent: {participant_1day.reminder_3days_sent}")
print(f"  - 1-day sent: {participant_1day.reminder_1day_sent}")

# Test management command (dry run)
print("\n5. Testing management command...")
from django.core.management import call_command
from io import StringIO

out = StringIO()
try:
    call_command('send_campaign_reminders', '--dry-run', stdout=out)
    output = out.getvalue()
    print("✅ Management command executed successfully")
    print("Command output:")
    print(output)
except Exception as e:
    print(f"❌ Management command failed: {e}")

print("\n" + "="*60)
print("REMINDER SYSTEM TEST COMPLETE")
print("="*60)

# Cleanup test campaigns
print("\nCleaning up test campaigns...")
campaign_3days.delete()
campaign_1day.delete()
print("✅ Test campaigns cleaned up")