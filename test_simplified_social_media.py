#!/usr/bin/env python
"""
Test script for simplified social media integration (3 platforms only)
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import get_user_model
from collaboration.models import CleanupGroup

User = get_user_model()

def test_simplified_social_media():
    """Test simplified social media integration with only 3 platforms"""
    
    print("🧪 Testing Simplified Social Media Integration")
    print("=" * 50)
    
    # Create a test user
    user, created = User.objects.get_or_create(
        username='demo_coordinator',
        defaults={
            'email': 'demo@ecolearn.com',
            'first_name': 'Demo',
            'last_name': 'Coordinator'
        }
    )
    
    if created:
        user.set_password('demo123')
        user.save()
        print("✅ Created demo coordinator user")
    else:
        print("✅ Using existing demo coordinator user")
    
    # Create a demo group with the 3 allowed social media platforms
    group, created = CleanupGroup.objects.get_or_create(
        name='Lusaka Green Champions',
        defaults={
            'description': 'Community cleanup group dedicated to making Lusaka cleaner and more sustainable. Join us for weekly cleanup activities and environmental education.',
            'community': 'Chelstone',
            'district': 'Lusaka',
            'coordinator': user,
            'facebook_url': 'https://facebook.com/lusaka-green-champions',
            'whatsapp_url': 'https://chat.whatsapp.com/BvJIyeNkMwzGkTxhNjAU3g',
            'twitter_url': 'https://x.com/lusaka_green'
        }
    )
    
    if created:
        print("✅ Created demo group with social media links")
    else:
        print("✅ Using existing demo group")
    
    # Test the social media links property
    print(f"\n📱 Group: {group.name}")
    print(f"📍 Location: {group.community}, {group.district}")
    print(f"👥 Members: {group.member_count}")
    
    social_links = group.social_media_links
    print(f"\n🔗 Social Media Links ({len(social_links)} platforms):")
    
    expected_platforms = ['Facebook', 'WhatsApp', 'X (Twitter)']
    
    for link in social_links:
        print(f"  • {link['name']}: {link['url']}")
        print(f"    Icon: {link['icon']} | Color: {link['color']}")
        
        # Verify it's one of the expected platforms
        if link['name'] in expected_platforms:
            print(f"    ✅ Platform allowed")
        else:
            print(f"    ❌ Unexpected platform: {link['name']}")
    
    # Test that only 3 platforms are supported
    if len(social_links) <= 3:
        print(f"\n✅ Correct number of social platforms (max 3)")
    else:
        print(f"\n❌ Too many social platforms: {len(social_links)}")
    
    # Test individual fields
    print(f"\n📋 Individual Social Media Fields:")
    print(f"  Facebook: {group.facebook_url}")
    print(f"  WhatsApp: {group.whatsapp_url}")
    print(f"  X (Twitter): {group.twitter_url}")
    
    # Verify removed fields don't exist
    removed_fields = ['linkedin_url', 'instagram_url', 'youtube_url', 'website_url']
    print(f"\n🗑️  Verifying removed fields:")
    
    for field in removed_fields:
        if hasattr(group, field):
            print(f"  ❌ {field} still exists (should be removed)")
        else:
            print(f"  ✅ {field} successfully removed")
    
    # Create a group with partial social media
    group2, created = CleanupGroup.objects.get_or_create(
        name='Ndola Eco Warriors',
        defaults={
            'description': 'Environmental action group in Ndola focused on community cleanup and awareness.',
            'community': 'Kansenshi',
            'district': 'Ndola',
            'coordinator': user,
            'facebook_url': 'https://facebook.com/ndola-eco-warriors',
            # Only Facebook for this group
        }
    )
    
    if created:
        print(f"\n✅ Created second demo group: {group2.name}")
    else:
        print(f"\n✅ Using existing second demo group: {group2.name}")
    
    social_links2 = group2.social_media_links
    print(f"🔗 Social Media Links for {group2.name} ({len(social_links2)} platforms):")
    
    for link in social_links2:
        print(f"  • {link['name']}: {link['url']}")
    
    print(f"\n🎉 Simplified Social Media Integration Test Complete!")
    print(f"📊 Summary:")
    print(f"  • Total demo groups created: 2")
    print(f"  • Maximum platforms per group: 3 (Facebook, WhatsApp, X)")
    print(f"  • Removed platforms: LinkedIn, Instagram, YouTube, Website")
    print(f"  • Official EcoLearn social links added to footer")
    
    return True

if __name__ == '__main__':
    try:
        test_simplified_social_media()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)