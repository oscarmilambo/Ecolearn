#!/usr/bin/env python3
"""
Fix CSRF verification issues
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings

def clear_sessions_and_cache():
    """Clear sessions and cache to fix CSRF issues"""
    print("🔧 Fixing CSRF verification issues...")
    
    try:
        # Clear sessions
        print("   - Clearing sessions...")
        call_command('clearsessions')
        
        # Clear cache if available
        try:
            from django.core.cache import cache
            cache.clear()
            print("   - Cache cleared")
        except:
            print("   - No cache to clear")
        
        print("✅ CSRF fix applied!")
        print("\n🔄 Please try these steps:")
        print("   1. Close your browser completely")
        print("   2. Clear browser cache/cookies")
        print("   3. Restart the Django server")
        print("   4. Try logging in again")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing CSRF: {e}")
        return False

def main():
    """Fix CSRF issues"""
    print("🚀 Fixing CSRF Verification Issues\n")
    
    success = clear_sessions_and_cache()
    
    if success:
        print(f"\n🎉 CSRF fix complete!")
        print(f"   Restart server: python manage.py runserver")
        print(f"   Then try: http://127.0.0.1:8000/admin/")

if __name__ == '__main__':
    main()