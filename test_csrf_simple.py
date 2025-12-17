#!/usr/bin/env python3
"""
Simple CSRF Test - No Redis dependency
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.conf import settings

def test_csrf_simple():
    """Simple CSRF test without Redis"""
    print("🔍 Simple CSRF Test")
    print("=" * 40)
    
    # Create test client
    client = Client(enforce_csrf_checks=True)
    
    # Test 1: Test login page (should not require login)
    print("\n1. Testing login page...")
    try:
        response = client.get('/accounts/login/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if 'csrfmiddlewaretoken' in content:
                print("   ✅ CSRF token found in login page")
                
                # Extract CSRF token
                import re
                csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
                    print(f"   ✅ CSRF token: {csrf_token[:20]}...")
                    
                    # Test POST to login with CSRF token
                    print("\n2. Testing POST with CSRF token...")
                    
                    # Create test user first
                    User = get_user_model()
                    user, created = User.objects.get_or_create(
                        username='testuser2',
                        defaults={
                            'email': 'test2@example.com',
                            'phone_number': '+260970000001'
                        }
                    )
                    
                    if created:
                        user.set_password('testpass123')
                        user.save()
                        print("   ✅ Test user created")
                    
                    # Test login POST
                    login_response = client.post('/accounts/login/', {
                        'username': 'testuser2',
                        'password': 'testpass123',
                        'csrfmiddlewaretoken': csrf_token
                    })
                    
                    print(f"   Login POST Status: {login_response.status_code}")
                    
                    if login_response.status_code == 302:
                        print("   ✅ Login successful (redirect)")
                    elif login_response.status_code == 403:
                        print("   ❌ CSRF verification failed on login")
                        content = login_response.content.decode('utf-8')
                        if 'CSRF verification failed' in content:
                            print("   ❌ Confirmed CSRF error in login")
                    else:
                        print(f"   ⚠️  Unexpected login status: {login_response.status_code}")
                        
                else:
                    print("   ❌ Could not extract CSRF token")
            else:
                print("   ❌ CSRF token not found in login page")
        else:
            print(f"   ❌ Login page failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Check if CSRF is working with a simple view
    print("\n3. Testing CSRF middleware directly...")
    
    from django.middleware.csrf import CsrfViewMiddleware
    from django.http import HttpRequest, HttpResponse
    
    # Create a mock request
    request = HttpRequest()
    request.method = 'POST'
    request.META['HTTP_HOST'] = 'localhost:8000'
    request.META['SERVER_NAME'] = 'localhost'
    request.META['SERVER_PORT'] = '8000'
    
    # Test CSRF middleware
    middleware = CsrfViewMiddleware(lambda req: HttpResponse('OK'))
    
    try:
        response = middleware(request)
        print(f"   CSRF Middleware response: {response.status_code}")
        
        if response.status_code == 403:
            print("   ✅ CSRF middleware is working (blocking POST without token)")
        else:
            print("   ⚠️  CSRF middleware response unexpected")
            
    except Exception as e:
        print(f"   ❌ CSRF middleware error: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Simple CSRF Test Complete!")

if __name__ == '__main__':
    test_csrf_simple()