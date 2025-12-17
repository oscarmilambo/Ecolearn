#!/usr/bin/env python3
"""
Detailed CSRF Debugging Script
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.middleware.csrf import get_token
from django.conf import settings

def test_csrf_detailed():
    """Detailed CSRF testing"""
    print("🔍 Detailed CSRF Testing")
    print("=" * 50)
    
    # Create test client
    client = Client()
    
    # Test 1: Get CSRF token from challenges page
    print("\n1. Testing GET request to challenges page...")
    try:
        response = client.get('/community/challenges/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for CSRF token in HTML
            if 'csrfmiddlewaretoken' in content:
                print("   ✅ CSRF token found in HTML")
                
                # Extract CSRF token
                import re
                csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
                    print(f"   ✅ CSRF token extracted: {csrf_token[:20]}...")
                else:
                    print("   ❌ Could not extract CSRF token value")
            else:
                print("   ❌ CSRF token not found in HTML")
                
            # Check for CSRF cookie
            if 'csrftoken' in response.cookies:
                csrf_cookie = response.cookies['csrftoken'].value
                print(f"   ✅ CSRF cookie found: {csrf_cookie[:20]}...")
            else:
                print("   ❌ CSRF cookie not found")
        else:
            print(f"   ❌ Failed to get challenges page: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Create a user and test POST request
    print("\n2. Testing POST request with user...")
    try:
        User = get_user_model()
        
        # Create or get test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'phone_number': '+260970000000'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            print("   ✅ Test user created")
        else:
            print("   ✅ Test user exists")
        
        # Login the user
        client.login(username='testuser', password='testpass123')
        print("   ✅ User logged in")
        
        # Get CSRF token
        csrf_token = get_token(client.session)
        print(f"   ✅ CSRF token from session: {csrf_token[:20]}...")
        
        # Test POST to join challenge (if challenges exist)
        from community.models import CommunityChallenge
        
        challenge = CommunityChallenge.objects.filter(is_active=True).first()
        if challenge:
            print(f"   ✅ Found test challenge: {challenge.title}")
            
            # Test POST with CSRF token
            response = client.post(
                f'/community/challenges/{challenge.id}/join/',
                data={'csrfmiddlewaretoken': csrf_token},
                HTTP_X_CSRFTOKEN=csrf_token
            )
            
            print(f"   POST Status: {response.status_code}")
            
            if response.status_code == 302:
                print("   ✅ POST successful (redirect)")
            elif response.status_code == 403:
                print("   ❌ CSRF verification failed")
                if hasattr(response, 'content'):
                    content = response.content.decode('utf-8')
                    if 'CSRF verification failed' in content:
                        print("   ❌ Confirmed CSRF error")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
        else:
            print("   ⚠️  No active challenges found for testing")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Check middleware order
    print("\n3. Checking middleware configuration...")
    middleware = settings.MIDDLEWARE
    csrf_index = -1
    session_index = -1
    auth_index = -1
    
    for i, mw in enumerate(middleware):
        if 'CsrfViewMiddleware' in mw:
            csrf_index = i
        elif 'SessionMiddleware' in mw:
            session_index = i
        elif 'AuthenticationMiddleware' in mw:
            auth_index = i
    
    print(f"   SessionMiddleware position: {session_index}")
    print(f"   CsrfViewMiddleware position: {csrf_index}")
    print(f"   AuthenticationMiddleware position: {auth_index}")
    
    if session_index < csrf_index < auth_index:
        print("   ✅ Middleware order is correct")
    else:
        print("   ❌ Middleware order may be incorrect")
    
    # Test 4: Check CSRF settings
    print("\n4. Checking CSRF settings...")
    print(f"   CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', 'Not set')}")
    print(f"   CSRF_COOKIE_HTTPONLY: {getattr(settings, 'CSRF_COOKIE_HTTPONLY', 'Not set')}")
    print(f"   CSRF_TRUSTED_ORIGINS: {getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'Not set')}")
    print(f"   DEBUG: {settings.DEBUG}")
    
    print("\n" + "=" * 50)
    print("🎉 CSRF Debugging Complete!")

if __name__ == '__main__':
    test_csrf_detailed()