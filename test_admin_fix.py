#!/usr/bin/env python
"""
Test script to verify CustomUser admin configuration is working
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib import admin
from accounts.models import CustomUser
from accounts.admin import CustomUserAdmin

def test_admin_configuration():
    """Test that CustomUserAdmin doesn't include date_joined in editable fields"""
    print("🔍 Testing CustomUser Admin Configuration...")
    print("=" * 50)
    
    # Get the admin class
    admin_class = admin.site._registry.get(CustomUser)
    
    if not admin_class:
        print("❌ CustomUser not registered in admin")
        return False
    
    print(f"✅ CustomUser admin class: {admin_class.__class__.__name__}")
    
    # Check fieldsets
    print("\n📋 Fieldsets:")
    for i, (name, options) in enumerate(admin_class.fieldsets):
        fields = options.get('fields', [])
        print(f"  {i+1}. {name or 'None'}: {fields}")
        
        if 'date_joined' in fields:
            print(f"❌ ERROR: date_joined found in fieldset '{name}'")
            return False
    
    # Check readonly fields
    print(f"\n🔒 Readonly fields: {admin_class.readonly_fields}")
    
    if 'date_joined' not in admin_class.readonly_fields:
        print("⚠️  WARNING: date_joined not in readonly_fields")
    
    # Check list display (this is OK)
    print(f"\n📊 List display: {admin_class.list_display}")
    
    print("\n✅ SUCCESS: date_joined is not in editable fieldsets")
    print("✅ Admin configuration should work now")
    return True

if __name__ == "__main__":
    try:
        success = test_admin_configuration()
        if success:
            print("\n🎉 Admin fix is working!")
            print("💡 You can now access /admin/accounts/customuser/ without errors")
        else:
            print("\n❌ Admin configuration still has issues")
    except Exception as e:
        print(f"❌ Error testing admin: {e}")
        import traceback
        traceback.print_exc()