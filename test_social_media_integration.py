#!/usr/bin/env python
"""
Test script for social media integration in collaboration groups
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

def test_social_media_integration():
    """Test social media integration functionality"""
    
    print("🧪 Testing Social Media Integration for Groups")
    print("=" * 50)
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_coordinator',
        defaults={
            'email': 'coordinator@test.com',
            'first_name': 'Test',
            'last_name': 'Coordinator'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Created test coordinator user")
    else:
        print("✅ Using existing test coordinator user")
    
    # Create a test group with social media links
    group, created = CleanupGroup.objects.get_or_create(
        name='EcoWarriors Lusaka',
        defaults={
            'description': 'Environmental cleanup group focused on making Lusaka cleaner and greener. Join us for weekly cleanup activities and community engagement.',
            'community': 'Kabulonga',
            'district': 'Lusaka',
            'coordinator': user,
            'facebook_url': 'https://facebook.com/ecowarriors-lusaka',
            'whatsapp_url': 'https://chat.whatsapp.com/BvJIyeNkMwzGkTxhNjAU3g',
            'twitter_url': 'https://twitter.com/ecowarriors_lsk',
            'linkedin_url': 'https://linkedin.com/company/ecowarriors-lusaka',
            'instagram_url': 'https://instagram.com/ecowarriors_lusaka',
            'youtube_url': 'https://youtube.com/channel/UCecowarriors',
            'website_url': 'https://ecowarriors-lusaka.org'
        }
    )
    
    if created:
        print("✅ Created test group with social media links")
    else:
        print("✅ Using existing test group")
    
    # Test social media links property
    print(f"\n📱 Group: {group.name}")
    print(f"📍 Location: {group.community}, {group.district}")
    print(f"👥 Members: {group.member_count}")
    
    social_links = group.social_media_links
    print(f"\n🔗 Social Media Links ({len(social_links)} platforms):")
    
    for link in social_links:
        print(f"  • {link['name']}: {link['url']}")
        print(f"    Icon: {link['icon']} | Color: {link['color']}")
    
    # Test individual fields
    print(f"\n📋 Individual Social Media Fields:")
    print(f"  Facebook: {group.facebook_url}")
    print(f"  WhatsApp: {group.whatsapp_url}")
    print(f"  Twitter: {group.twitter_url}")
    print(f"  LinkedIn: {group.linkedin_url}")
    print(f"  Instagram: {group.instagram_url}")
    print(f"  YouTube: {group.youtube_url}")
    print(f"  Website: {group.website_url}")
    
    # Create another group with partial social media
    group2, created = CleanupGroup.objects.get_or_create(
        name='Green Ndola Initiative',
        defaults={
            'description': 'Community-driven environmental initiative in Ndola focusing on waste management and tree planting.',
            'community': 'Masala',
            'district': 'Ndola',
            'coordinator': user,
            'facebook_url': 'https://facebook.com/green-ndola',
            'whatsapp_url': 'https://chat.whatsapp.com/invite123',
            # Only Facebook and WhatsApp for this group
        }
    )
    
    if created:
        print(f"\n✅ Created second test group: {group2.name}")
    else:
        print(f"\n✅ Using existing second test group: {group2.name}")
    
    social_links2 = group2.social_media_links
    print(f"🔗 Social Media Links for {group2.name} ({len(social_links2)} platforms):")
    
    for link in social_links2:
        print(f"  • {link['name']}: {link['url']}")
    
    # Test group with no social media
    group3, created = CleanupGroup.objects.get_or_create(
        name='Kitwe Clean Team',
        defaults={
            'description': 'Local cleanup team in Kitwe working on community beautification projects.',
            'community': 'Riverside',
            'district': 'Kitwe',
            'coordinator': user,
            # No social media links
        }
    )
    
    if created:
        print(f"\n✅ Created third test group: {group3.name}")
    else:
        print(f"\n✅ Using existing third test group: {group3.name}")
    
    social_links3 = group3.social_media_links
    print(f"🔗 Social Media Links for {group3.name} ({len(social_links3)} platforms):")
    
    if not social_links3:
        print("  No social media links configured")
    
    print(f"\n🎉 Social Media Integration Test Complete!")
    print(f"📊 Summary:")
    print(f"  • Total groups tested: 3")
    print(f"  • Groups with social media: {len([g for g in [group, group2, group3] if g.social_media_links])}")
    print(f"  • Total social platforms configured: {sum(len(g.social_media_links) for g in [group, group2, group3])}")
    
    return True

if __name__ == '__main__':
    try:
        test_social_media_integration()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)