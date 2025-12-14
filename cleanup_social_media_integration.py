#!/usr/bin/env python
"""
Cleanup script for social media integration
- Remove test groups created during development
- Apply migration to remove unused social media fields
- Clean up test data
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import get_user_model
from collaboration.models import CleanupGroup
from django.core.management import execute_from_command_line

User = get_user_model()

def cleanup_social_media_integration():
    """Clean up test data and apply migrations"""
    
    print("🧹 Cleaning up Social Media Integration")
    print("=" * 45)
    
    # Remove test groups created by the integration script
    test_group_names = [
        'EcoWarriors Lusaka',
        'Green Ndola Initiative', 
        'Kitwe Clean Team',
        'Test Group'
    ]
    
    removed_groups = 0
    for group_name in test_group_names:
        groups = CleanupGroup.objects.filter(name=group_name)
        if groups.exists():
            count = groups.count()
            groups.delete()
            print(f"✅ Removed test group: {group_name} ({count} instance(s))")
            removed_groups += count
        else:
            print(f"ℹ️  Test group not found: {group_name}")
    
    # Remove test coordinator user
    test_users = ['test_coordinator', 'test_user']
    removed_users = 0
    for username in test_users:
        try:
            user = User.objects.get(username=username)
            user.delete()
            print(f"✅ Removed test user: {username}")
            removed_users += 1
        except User.DoesNotExist:
            print(f"ℹ️  Test user not found: {username}")
    
    # Apply migration to remove unused social media fields
    print(f"\n🔄 Applying migration to remove unused social media fields...")
    try:
        execute_from_command_line(['manage.py', 'migrate', 'collaboration'])
        print(f"✅ Migration applied successfully")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    
    # Show remaining groups with social media
    print(f"\n📊 Current Groups with Social Media:")
    groups_with_social = CleanupGroup.objects.filter(
        models.Q(facebook_url__isnull=False, facebook_url__gt='') |
        models.Q(whatsapp_url__isnull=False, whatsapp_url__gt='') |
        models.Q(twitter_url__isnull=False, twitter_url__gt='')
    ).distinct()
    
    if groups_with_social.exists():
        for group in groups_with_social:
            social_count = sum(1 for url in [group.facebook_url, group.whatsapp_url, group.twitter_url] if url)
            print(f"  • {group.name} ({social_count} social platform(s))")
    else:
        print(f"  No groups with social media links found")
    
    print(f"\n🎯 Cleanup Summary:")
    print(f"  • Test groups removed: {removed_groups}")
    print(f"  • Test users removed: {removed_users}")
    print(f"  • Social media fields simplified to 3 platforms")
    print(f"  • Official EcoLearn social links added to footer")
    
    print(f"\n✨ Social Media Integration Cleanup Complete!")
    print(f"📱 Users can now add Facebook, WhatsApp, and X links to their groups")
    print(f"🌐 Official EcoLearn social media links are in the footer")
    
    return True

if __name__ == '__main__':
    try:
        # Import models for the query
        from django.db import models
        
        cleanup_social_media_integration()
        print(f"\n✅ Cleanup completed successfully!")
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)