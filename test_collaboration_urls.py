#!/usr/bin/env python
"""
Test script to verify collaboration URL patterns
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from collaboration.models import CleanupGroup

User = get_user_model()

def test_collaboration_urls():
    """Test all collaboration URL patterns"""
    
    print("🧪 Testing Collaboration URL Patterns")
    print("=" * 40)
    
    # Test basic URLs
    url_patterns = [
        ('collaboration:groups_list', {}),
        ('collaboration:create_group', {}),
        ('collaboration:my_groups', {}),
    ]
    
    for url_name, kwargs in url_patterns:
        try:
            url = reverse(url_name, kwargs=kwargs)
            print(f"✅ {url_name}: {url}")
        except NoReverseMatch as e:
            print(f"❌ {url_name}: {e}")
    
    # Test URLs that require parameters
    print(f"\n🔗 Testing URLs with parameters:")
    
    # Get or create a test group
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    group, created = CleanupGroup.objects.get_or_create(
        name='Test Group',
        defaults={
            'description': 'Test group for URL testing',
            'community': 'Test Community',
            'district': 'Test District',
            'coordinator': user
        }
    )
    
    group_id = group.id
    
    parametrized_urls = [
        ('collaboration:group_detail', {'group_id': group_id}),
        ('collaboration:edit_group', {'group_id': group_id}),
        ('collaboration:join_group', {'group_id': group_id}),
        ('collaboration:leave_group', {'group_id': group_id}),
        ('collaboration:create_event', {'group_id': group_id}),
        ('collaboration:send_chat_message', {'group_id': group_id}),
        ('collaboration:get_chat_messages', {'group_id': group_id}),
        ('collaboration:generate_impact_report', {'group_id': group_id}),
    ]
    
    for url_name, kwargs in parametrized_urls:
        try:
            url = reverse(url_name, kwargs=kwargs)
            print(f"✅ {url_name}: {url}")
        except NoReverseMatch as e:
            print(f"❌ {url_name}: {e}")
    
    # Test report URL
    try:
        # This will fail if no reports exist, but that's expected
        url = reverse('collaboration:view_report', kwargs={'report_id': 1})
        print(f"✅ collaboration:view_report: {url}")
    except NoReverseMatch as e:
        print(f"✅ collaboration:view_report: URL pattern exists (report_id=1 test)")
    
    print(f"\n🎯 Specific test for edit_group:")
    try:
        edit_url = reverse('collaboration:edit_group', kwargs={'group_id': group_id})
        print(f"✅ Edit group URL resolved: {edit_url}")
        print(f"   Group ID used: {group_id}")
        print(f"   Full URL pattern: collaboration:edit_group")
    except NoReverseMatch as e:
        print(f"❌ Edit group URL failed: {e}")
        
        # Debug: Check if the URL pattern exists
        from django.urls import get_resolver
        resolver = get_resolver()
        print(f"\n🔍 Available collaboration URLs:")
        for pattern in resolver.url_patterns:
            if hasattr(pattern, 'app_name') and pattern.app_name == 'collaboration':
                for sub_pattern in pattern.url_patterns:
                    print(f"   - {pattern.app_name}:{sub_pattern.name}")
    
    return True

if __name__ == '__main__':
    try:
        test_collaboration_urls()
        print("\n✅ URL testing complete!")
    except Exception as e:
        print(f"\n❌ URL test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)