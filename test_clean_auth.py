#!/usr/bin/env python3
"""
Test script to verify clean email/password authentication works
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from accounts.models import CustomUser

def test_clean_authentication():
    """Test that authentication works without Google OAuth"""
    
    print("🧪 Testing Clean Authentication System")
    print("=" * 50)
    
    client = Client()
    
    # 1. Test registration page loads
    print("\n1️⃣ Testing registration page...")
    try:
        response = client.get(reverse('accounts:register'))
        if response.status_code == 200:
            print("✅ Registration page loads successfully")
            
            # Check that no Google OAuth elements exist
            content = response.content.decode()
            if 'google' not in content.lower() and 'socialaccount' not in content:
                print("✅ No Google OAuth elements found in registration")
            else:
                print("❌ Google OAuth elements still present")
        else:
            print(f"❌ Registration page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Registration page error: {e}")
    
    # 2. Test login page loads
    print("\n2️⃣ Testing login page...")
    try:
        response = client.get(reverse('accounts:login'))
        if response.status_code == 200:
            print("✅ Login page loads successfully")
            
            # Check that no Google OAuth elements exist
            content = response.content.decode()
            if 'google' not in content.lower() and 'socialaccount' not in content:
                print("✅ No Google OAuth elements found in login")
            else:
                print("❌ Google OAuth elements still present")
        else:
            print(f"❌ Login page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Login page error: {e}")
    
    # 3. Test user registration
    print("\n3️⃣ Testing user registration...")
    try:
        # Clean up any existing test user
        CustomUser.objects.filter(email='test@example.com').delete()
        
        registration_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'gender': 'male',
            'contact_method': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = client.post(reverse('accounts:register'), registration_data)
        
        if response.status_code in [200, 302]:  # Success or redirect
            print("✅ Registration form submission successful")
            
            # Check if user was created
            if CustomUser.objects.filter(email='test@example.com').exists():
                print("✅ User created successfully in database")
            else:
                print("❌ User not found in database")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            if hasattr(response, 'context') and response.context:
                form = response.context.get('form')
                if form and form.errors:
                    print(f"   Form errors: {form.errors}")
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    # 4. Test settings configuration
    print("\n4️⃣ Testing settings configuration...")
    from django.conf import settings
    
    installed_apps = settings.INSTALLED_APPS
    if 'allauth.socialaccount' not in installed_apps:
        print("✅ socialaccount app removed from INSTALLED_APPS")
    else:
        print("❌ socialaccount app still in INSTALLED_APPS")
    
    if 'allauth.socialaccount.providers.google' not in installed_apps:
        print("✅ Google provider removed from INSTALLED_APPS")
    else:
        print("❌ Google provider still in INSTALLED_APPS")
    
    if not hasattr(settings, 'SOCIALACCOUNT_PROVIDERS'):
        print("✅ SOCIALACCOUNT_PROVIDERS setting removed")
    else:
        print("❌ SOCIALACCOUNT_PROVIDERS setting still exists")
    
    if not hasattr(settings, 'SOCIALACCOUNT_ADAPTER'):
        print("✅ SOCIALACCOUNT_ADAPTER setting removed")
    else:
        print("❌ SOCIALACCOUNT_ADAPTER setting still exists")
    
    print("\n" + "=" * 50)
    print("🎉 Clean authentication test completed!")

if __name__ == '__main__':
    test_clean_authentication()