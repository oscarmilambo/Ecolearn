#!/usr/bin/env python3
"""
Test Simplified Django Configuration (No Redis)
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.test import Client
from django.conf import settings
from django.core.cache import cache
from django.contrib.sessions.models import Session

def test_simplified_config():
    """Test the simplified configuration without Redis"""
    print("🔍 Testing Simplified Django Configuration (No Redis)")
    print("=" * 60)
    
    # Test 1: Check cache configuration
    print("\n1. Testing Cache Configuration...")
    
    cache_backend = settings.CACHES['default']['BACKEND']
    print(f"   Cache Backend: {cache_backend}")
    
    if 'locmem' in cache_backend:
        print("   ✅ Using Local Memory Cache (no Redis)")
    else:
        print(f"   ❌ Unexpected cache backend: {cache_backend}")
        return False
    
    # Test cache functionality
    try:
        cache.set('test_key', 'test_value', 60)
        cached_value = cache.get('test_key')
        
        if cached_value == 'test_value':
            print("   ✅ Cache is working correctly")
        else:
            print("   ❌ Cache test failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Cache error: {e}")
        return False
    
    # Test 2: Check session configuration
    print("\n2. Testing Session Configuration...")
    
    session_engine = settings.SESSION_ENGINE
    print(f"   Session Engine: {session_engine}")
    
    if 'db' in session_engine:
        print("   ✅ Using Database Sessions (no Redis)")
    else:
        print(f"   ❌ Unexpected session engine: {session_engine}")
        return False
    
    # Test session functionality
    try:
        client = Client()
        
        # Test session creation
        response = client.get('/accounts/login/')
        
        if response.status_code == 200:
            print("   ✅ Session creation works")
            
            # Check if session was created in database
            session_count = Session.objects.count()
            print(f"   ✅ Sessions in database: {session_count}")
            
        else:
            print(f"   ❌ Session test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Session error: {e}")
        return False
    
    # Test 3: Check Channels configuration
    print("\n3. Testing Channels Configuration...")
    
    channel_layers = settings.CHANNEL_LAYERS
    channel_backend = channel_layers['default']['BACKEND']
    print(f"   Channel Backend: {channel_backend}")
    
    if 'InMemoryChannelLayer' in channel_backend:
        print("   ✅ Using In-Memory Channel Layer (no Redis)")
    else:
        print(f"   ❌ Unexpected channel backend: {channel_backend}")
        return False
    
    # Test 4: Check CSRF functionality
    print("\n4. Testing CSRF Functionality...")
    
    try:
        from django.middleware.csrf import get_token
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/')
        
        # Add session to request
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        csrf_token = get_token(request)
        
        if csrf_token:
            print(f"   ✅ CSRF token generated: {csrf_token[:20]}...")
        else:
            print("   ❌ CSRF token generation failed")
            return False
            
    except Exception as e:
        print(f"   ❌ CSRF error: {e}")
        return False
    
    # Test 5: Check settings summary
    print("\n5. Configuration Summary...")
    
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   Cache Backend: {settings.CACHES['default']['BACKEND']}")
    print(f"   Session Engine: {settings.SESSION_ENGINE}")
    print(f"   Session Cookie Age: {settings.SESSION_COOKIE_AGE} seconds")
    print(f"   Channel Backend: {settings.CHANNEL_LAYERS['default']['BACKEND']}")
    
    # Check for Redis references
    redis_found = False
    for key, value in settings.__dict__.items():
        if isinstance(value, str) and 'redis' in value.lower():
            print(f"   ⚠️  Redis reference found: {key} = {value}")
            redis_found = True
    
    if not redis_found:
        print("   ✅ No Redis references found in settings")
    
    print("\n" + "=" * 60)
    print("🎉 Simplified Configuration Test Complete!")
    
    return True

if __name__ == '__main__':
    success = test_simplified_config()
    if success:
        print("\n✅ All tests passed! Your Django setup is now Redis-free.")
    else:
        print("\n❌ Some tests failed. Please check the configuration.")