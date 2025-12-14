#!/usr/bin/env python3
"""
Simple test to verify clean authentication system
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

def test_settings():
    """Test that settings are properly cleaned"""
    
    print("🧪 Testing Clean Authentication Settings")
    print("=" * 50)
    
    from django.conf import settings
    
    # Check INSTALLED_APPS
    installed_apps = settings.INSTALLED_APPS
    
    print("\n📦 Checking INSTALLED_APPS...")
    if 'allauth' in installed_apps:
        print("✅ allauth (core) is installed")
    else:
        print("❌ allauth (core) is missing")
    
    if 'allauth.account' in installed_apps:
        print("✅ allauth.account is installed")
    else:
        print("❌ allauth.account is missing")
    
    if 'allauth.socialaccount' not in installed_apps:
        print("✅ allauth.socialaccount removed")
    else:
        print("❌ allauth.socialaccount still present")
    
    if 'allauth.socialaccount.providers.google' not in installed_apps:
        print("✅ Google provider removed")
    else:
        print("❌ Google provider still present")
    
    # Check settings
    print("\n⚙️ Checking settings...")
    
    if hasattr(settings, 'ACCOUNT_ADAPTER'):
        print("✅ ACCOUNT_ADAPTER is configured")
    else:
        print("❌ ACCOUNT_ADAPTER is missing")
    
    if not hasattr(settings, 'SOCIALACCOUNT_ADAPTER'):
        print("✅ SOCIALACCOUNT_ADAPTER removed")
    else:
        print("❌ SOCIALACCOUNT_ADAPTER still present")
    
    if not hasattr(settings, 'SOCIALACCOUNT_PROVIDERS'):
        print("✅ SOCIALACCOUNT_PROVIDERS removed")
    else:
        print("❌ SOCIALACCOUNT_PROVIDERS still present")
    
    # Check authentication backends
    print("\n🔐 Checking authentication backends...")
    auth_backends = settings.AUTHENTICATION_BACKENDS
    
    if 'django.contrib.auth.backends.ModelBackend' in auth_backends:
        print("✅ Django ModelBackend present")
    else:
        print("❌ Django ModelBackend missing")
    
    if 'allauth.account.auth_backends.AuthenticationBackend' in auth_backends:
        print("✅ Allauth AuthenticationBackend present")
    else:
        print("❌ Allauth AuthenticationBackend missing")
    
    print("\n" + "=" * 50)
    print("🎉 Settings verification completed!")

def test_forms():
    """Test that forms work correctly"""
    
    print("\n📝 Testing Registration Form...")
    
    from accounts.forms import CustomUserCreationForm
    
    # Test form with valid data
    form_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'gender': 'male',
        'contact_method': 'test@example.com',
        'password': 'testpass123'
    }
    
    form = CustomUserCreationForm(data=form_data)
    
    if form.is_valid():
        print("✅ Registration form validates correctly")
    else:
        print("❌ Registration form validation failed")
        print(f"   Errors: {form.errors}")
    
    # Check that email field exists
    if 'email' in form.fields:
        print("✅ Email field present in form")
    else:
        print("❌ Email field missing from form")

if __name__ == '__main__':
    test_settings()
    test_forms()