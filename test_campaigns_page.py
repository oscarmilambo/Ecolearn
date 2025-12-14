#!/usr/bin/env python
"""
Test script to verify campaigns page is working
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from community.models import CommunityCampaign
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# Create test client
client = Client()

# Get or create test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"✅ Created test user: {user.username}")
else:
    print(f"✅ Using existing user: {user.username}")

# Login
login_success = client.login(username='testuser', password='testpass123')
print(f"✅ Login successful: {login_success}")

# Test campaigns list page
print("\n🔍 Testing campaigns list page...")
response = client.get('/community/campaigns/')
print(f"Status Code: {response.status_code}")
print(f"Content Type: {response.get('Content-Type', 'N/A')}")

if response.status_code == 200:
    print("✅ Campaigns page loaded successfully!")
    
    # Check if template rendered
    if hasattr(response, 'templates'):
        print(f"Templates used: {[t.name for t in response.templates]}")
    
    # Check context
    if hasattr(response, 'context'):
        print(f"\nContext variables:")
        print(f"  - upcoming_campaigns: {len(response.context.get('upcoming_campaigns', []))}")
        print(f"  - ongoing_campaigns: {len(response.context.get('ongoing_campaigns', []))}")
        print(f"  - past_campaigns: {len(response.context.get('past_campaigns', []))}")
        print(f"  - user_campaigns: {len(response.context.get('user_campaigns', []))}")
    
    # Check for campaigns in database
    total_campaigns = CommunityCampaign.objects.filter(is_active=True, is_published=True).count()
    print(f"\n📊 Total active campaigns in database: {total_campaigns}")
    
    if total_campaigns == 0:
        print("\n⚠️  No campaigns found. Creating a test campaign...")
        
        # Create a test campaign
        campaign = CommunityCampaign.objects.create(
            title="Test Community Cleanup",
            description="A test campaign for community cleanup activities",
            campaign_type="cleanup",
            location="Lusaka, Zambia",
            start_date=timezone.now() + timedelta(days=7),
            end_date=timezone.now() + timedelta(days=7, hours=4),
            recurrence="one_time",
            is_active=True,
            is_published=True
        )
        print(f"✅ Created test campaign: {campaign.title}")
        print(f"   Start: {campaign.start_date}")
        print(f"   Location: {campaign.location}")
        
        # Test again
        response = client.get('/community/campaigns/')
        if response.status_code == 200:
            print("\n✅ Page loads successfully with test campaign!")
        
else:
    print(f"❌ Error loading campaigns page!")
    print(f"Response content (first 500 chars):")
    print(response.content.decode('utf-8')[:500])

print("\n" + "="*60)
print("Test complete!")
