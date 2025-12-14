#!/usr/bin/env python
"""
Diagnose campaigns page issues
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from community.models import CommunityCampaign
from django.utils import timezone

print("="*60)
print("CAMPAIGNS DIAGNOSTIC")
print("="*60)

# Check if campaigns exist
print("\n1. Checking database for campaigns...")
all_campaigns = CommunityCampaign.objects.all()
print(f"   Total campaigns: {all_campaigns.count()}")

active_campaigns = CommunityCampaign.objects.filter(is_active=True)
print(f"   Active campaigns: {active_campaigns.count()}")

published_campaigns = CommunityCampaign.objects.filter(is_active=True, is_published=True)
print(f"   Published campaigns: {published_campaigns.count()}")

# Check upcoming campaigns
upcoming = CommunityCampaign.objects.filter(
    is_active=True,
    is_published=True,
    start_date__gte=timezone.now()
).order_by('start_date')
print(f"   Upcoming campaigns: {upcoming.count()}")

# Check ongoing campaigns
ongoing = CommunityCampaign.objects.filter(
    is_active=True,
    is_published=True,
    start_date__lte=timezone.now(),
    end_date__gte=timezone.now()
).order_by('start_date')
print(f"   Ongoing campaigns: {ongoing.count()}")

# Check past campaigns
past = CommunityCampaign.objects.filter(
    is_active=True,
    is_published=True,
    end_date__lt=timezone.now()
).order_by('-start_date')[:5]
print(f"   Past campaigns: {past.count()}")

# List all campaigns
if all_campaigns.exists():
    print("\n2. Campaign details:")
    for campaign in all_campaigns[:10]:
        print(f"\n   📅 {campaign.title}")
        print(f"      Type: {campaign.campaign_type}")
        print(f"      Location: {campaign.location}")
        print(f"      Start: {campaign.start_date}")
        print(f"      End: {campaign.end_date}")
        print(f"      Active: {campaign.is_active}")
        print(f"      Published: {campaign.is_published}")
        print(f"      Participants: {campaign.participant_count}")
else:
    print("\n2. ⚠️  No campaigns found in database!")
    print("   You need to create campaigns in the admin panel.")
    print("   Go to: http://localhost:8000/admin/community/communitycampaign/")

# Check URL configuration
print("\n3. Checking URL configuration...")
try:
    from django.urls import reverse
    campaigns_url = reverse('community:campaigns_list')
    print(f"   ✅ Campaigns URL: {campaigns_url}")
    
    calendar_url = reverse('community:campaign_calendar')
    print(f"   ✅ Calendar URL: {calendar_url}")
except Exception as e:
    print(f"   ❌ URL Error: {e}")

# Check view function
print("\n4. Checking view function...")
try:
    from community.views import campaigns_list
    print(f"   ✅ View function exists: {campaigns_list.__name__}")
except Exception as e:
    print(f"   ❌ View Error: {e}")

# Check template
print("\n5. Checking template...")
import os
template_path = "community/templates/community/campaigns_list.html"
if os.path.exists(template_path):
    print(f"   ✅ Template exists: {template_path}")
else:
    print(f"   ❌ Template not found: {template_path}")

print("\n" + "="*60)
print("RECOMMENDATIONS:")
print("="*60)

if not published_campaigns.exists():
    print("\n⚠️  No published campaigns found!")
    print("\nTo fix:")
    print("1. Go to admin panel: http://localhost:8000/admin/")
    print("2. Navigate to: Community → Community campaigns")
    print("3. Create a new campaign or edit existing ones")
    print("4. Make sure to:")
    print("   - Set 'Is active' to checked")
    print("   - Set 'Is published' to checked")
    print("   - Set future dates for upcoming campaigns")
else:
    print("\n✅ Campaigns are configured correctly!")
    print("\nIf you're still seeing a white page:")
    print("1. Restart your Django development server")
    print("2. Clear your browser cache (Ctrl+Shift+Delete)")
    print("3. Try accessing: http://localhost:8000/community/campaigns/")
    print("4. Check browser console for JavaScript errors (F12)")

print("\n" + "="*60)
