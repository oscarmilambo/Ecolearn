#!/usr/bin/env python
"""
Test campaign calendar functionality
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from community.models import CommunityCampaign
import json

User = get_user_model()

print("="*60)
print("TESTING CAMPAIGN CALENDAR")
print("="*60)

# Get or create test user
user, created = User.objects.get_or_create(
    username='calendaruser',
    defaults={
        'email': 'calendar@example.com',
        'first_name': 'Calendar',
        'last_name': 'User'
    }
)
if created:
    user.set_password('calendarpass123')
    user.save()

# Test with client
client = Client()
client.force_login(user)

print(f"Testing as user: {user.username}")

# Test calendar page
print("\n1. Testing calendar page...")
response = client.get('/community/campaigns/calendar/', HTTP_HOST='localhost')
print(f"   Status code: {response.status_code}")

if response.status_code == 200:
    print("   ✅ Calendar page loads successfully!")
    
    content = response.content.decode('utf-8')
    
    # Check for key elements
    if 'Campaign Calendar' in content:
        print("   ✅ Contains calendar title")
    if 'fullcalendar' in content.lower():
        print("   ✅ FullCalendar library loaded")
    if 'calendar_events' in content:
        print("   ✅ Calendar events data present")
    
    # Check context
    if hasattr(response, 'context') and response.context:
        campaigns = response.context.get('campaigns', [])
        calendar_events = response.context.get('calendar_events', '[]')
        
        print(f"   📊 Campaigns in context: {len(campaigns) if hasattr(campaigns, '__len__') else 'N/A'}")
        
        try:
            events_data = json.loads(calendar_events)
            print(f"   📊 Calendar events: {len(events_data)}")
            
            if events_data:
                print("   📅 Sample event:")
                event = events_data[0]
                print(f"      Title: {event.get('title', 'N/A')}")
                print(f"      Start: {event.get('start', 'N/A')}")
                print(f"      Location: {event.get('location', 'N/A')}")
                print(f"      Type: {event.get('type', 'N/A')}")
        except json.JSONDecodeError as e:
            print(f"   ❌ Calendar events JSON error: {e}")
    
else:
    print(f"   ❌ Calendar page failed: {response.status_code}")
    if hasattr(response, 'content'):
        print(f"   Error content: {response.content.decode('utf-8')[:500]}")

# Test campaigns exist
print("\n2. Checking campaigns in database...")
campaigns = CommunityCampaign.objects.filter(is_active=True, is_published=True)
print(f"   Active campaigns: {campaigns.count()}")

for i, campaign in enumerate(campaigns[:3], 1):
    print(f"   {i}. {campaign.title}")
    print(f"      Start: {campaign.start_date}")
    print(f"      Location: {campaign.location}")
    print(f"      Type: {campaign.campaign_type}")
    
    # Test get_absolute_url
    try:
        url = campaign.get_absolute_url()
        print(f"      URL: {url}")
    except Exception as e:
        print(f"      ❌ URL error: {e}")

print("\n" + "="*60)
print("CALENDAR TEST COMPLETE")
print("="*60)