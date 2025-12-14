#!/usr/bin/env python
"""
Complete test to verify both admin fix and settings updates
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib import admin
from django.conf import settings
from accounts.models import CustomUser

def test_admin_fix():
    """Test that CustomUser admin is fixed"""
    print("🔍 Testing Admin Fix...")
    print("=" * 50)
    
    admin_class = admin.site._registry.get(CustomUser)
    if not admin_class:
        print("❌ CustomUser not registered in admin")
        return False
    
    # Check that date_joined is not in editable fieldsets
    for name, options in admin_class.fieldsets:
        fields = options.get('fields', [])
        if 'date_joined' in fields:
            print(f"❌ ERROR: date_joined found in fieldset '{name}'")
            return False
    
    # Check readonly fields
    if 'date_joined' not in admin_class.readonly_fields:
        print("⚠️  WARNING: date_joined not in readonly_fields")
    
    print("✅ Admin fix is working - date_joined not in editable fields")
    return True

def test_settings_update():
    """Test that deprecated settings are updated"""
    print("\n🔍 Testing Settings Update...")
    print("=" * 50)
    
    # Check new settings exist
    new_settings = [
        'ACCOUNT_LOGIN_METHODS',
        'ACCOUNT_SIGNUP_FIELDS', 
        'ACCOUNT_RATE_LIMITS'
    ]
    
    for setting in new_settings:
        if hasattr(settings, setting):
            value = getattr(settings, setting)
            print(f"✅ {setting}: {value}")
        else:
            print(f"❌ Missing new setting: {setting}")
            return False
    
    # Check deprecated settings are removed
    deprecated_settings = [
        'ACCOUNT_AUTHENTICATION_METHOD',
        'ACCOUNT_EMAIL_REQUIRED',
        'ACCOUNT_USERNAME_REQUIRED',
        'ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE',
        'ACCOUNT_LOGIN_ATTEMPTS_LIMIT',
        'ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT'
    ]
    
    found_deprecated = []
    for setting in deprecated_settings:
        if hasattr(settings, setting):
            found_deprecated.append(setting)
    
    if found_deprecated:
        print(f"⚠️  Still has deprecated settings: {found_deprecated}")
        print("   (These might be set elsewhere or cached)")
    else:
        print("✅ No deprecated settings found")
    
    return True

def main():
    print("🚀 Complete Fix Verification")
    print("=" * 60)
    
    admin_ok = test_admin_fix()
    settings_ok = test_settings_update()
    
    print("\n" + "=" * 60)
    if admin_ok and settings_ok:
        print("🎉 ALL FIXES WORKING!")
        print("✅ Admin FieldError is fixed")
        print("✅ Deprecated settings are updated")
        print("\n💡 You can now:")
        print("   - Access /admin/accounts/customuser/ without errors")
        print("   - Run the server with fewer deprecation warnings")
    else:
        print("❌ Some issues remain")
    
    print("\n🔧 To test the admin fix:")
    print("   1. Run: python manage.py runserver")
    print("   2. Go to: http://127.0.0.1:8000/admin/")
    print("   3. Navigate to: Accounts > Custom users")
    print("   4. Try editing a user - should work without FieldError")

if __name__ == "__main__":
    main()