#!/usr/bin/env python
"""
Fix script for collaboration URLs issue
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.urls import reverse
from django.core.management import execute_from_command_line

def fix_urls():
    """Fix collaboration URLs issue"""
    
    print("🔧 Fixing Collaboration URLs Issue")
    print("=" * 40)
    
    # Test URL resolution
    try:
        url = reverse('collaboration:edit_group', kwargs={'group_id': 1})
        print(f"✅ URL resolution works: {url}")
        print("The issue is likely that the Django server needs to be restarted.")
        print("\n💡 Solution:")
        print("1. Stop the Django development server (Ctrl+C)")
        print("2. Restart it with: python manage.py runserver")
        print("3. The edit_group URL should now work correctly")
        
    except Exception as e:
        print(f"❌ URL resolution failed: {e}")
        print("\n🔍 Checking URL patterns...")
        
        # Import and check URL patterns
        from django.urls import get_resolver
        from django.urls.exceptions import NoReverseMatch
        
        resolver = get_resolver()
        
        # Find collaboration app URLs
        collaboration_patterns = []
        for pattern in resolver.url_patterns:
            if hasattr(pattern, 'app_name') and pattern.app_name == 'collaboration':
                for sub_pattern in pattern.url_patterns:
                    collaboration_patterns.append(f"{pattern.app_name}:{sub_pattern.name}")
        
        print(f"Available collaboration URLs:")
        for pattern in collaboration_patterns:
            print(f"  - {pattern}")
        
        if 'collaboration:edit_group' not in collaboration_patterns:
            print(f"\n❌ edit_group URL pattern is missing!")
            print(f"Need to check collaboration/urls.py")
        else:
            print(f"\n✅ edit_group URL pattern exists")
            print(f"The issue might be with the view function or imports")
    
    # Check if view function exists
    try:
        from collaboration.views import edit_group
        print(f"✅ edit_group view function exists")
    except ImportError as e:
        print(f"❌ edit_group view function missing: {e}")
    
    # Collect static files and check for any issues
    print(f"\n🔄 Running Django checks...")
    try:
        execute_from_command_line(['manage.py', 'check'])
        print(f"✅ Django checks passed")
    except Exception as e:
        print(f"❌ Django checks failed: {e}")
    
    return True

if __name__ == '__main__':
    try:
        fix_urls()
        print(f"\n🎯 Summary:")
        print(f"The most likely solution is to restart the Django development server.")
        print(f"If the issue persists, check the server console for any import errors.")
    except Exception as e:
        print(f"\n❌ Fix script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)