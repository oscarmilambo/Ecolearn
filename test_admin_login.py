#!/usr/bin/env python
"""
Test admin login functionality
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model
from django.test import Client

def test_admin_login():
    """Test admin login functionality"""
    print("🔍 Testing admin login...")
    
    User = get_user_model()
    
    # Check if admin user exists
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Admin user found - ID: {admin_user.id}")
        print(f"   Is superuser: {admin_user.is_superuser}")
        print(f"   Is staff: {admin_user.is_staff}")
        print(f"   Is active: {admin_user.is_active}")
    except User.DoesNotExist:
        print("❌ Admin user not found")
        return False
    
    # Test authentication
    user = authenticate(username='admin', password='admin123')
    if user:
        print("✅ Authentication successful")
        print(f"   Authenticated user ID: {user.id}")
    else:
        print("❌ Authentication failed")
        return False
    
    # Test login via Django test client
    client = Client()
    response = client.post('/accounts/login/', {
        'username': 'admin',
        'password': 'admin123'
    })
    
    if response.status_code == 302:  # Redirect after successful login
        print("✅ Login form submission successful (redirected)")
        print(f"   Redirect location: {response.get('Location', 'Not specified')}")
    elif response.status_code == 200:
        print("⚠️  Login form returned 200 (check for form errors)")
        # Check if there are form errors in the response
        if b'invalid' in response.content.lower() or b'error' in response.content.lower():
            print("❌ Login form contains error messages")
            return False
        else:
            print("✅ Login form processed without errors")
    else:
        print(f"❌ Unexpected response status: {response.status_code}")
        return False
    
    print("🎉 Admin login test completed successfully!")
    return True

if __name__ == '__main__':
    success = test_admin_login()
    sys.exit(0 if success else 1)