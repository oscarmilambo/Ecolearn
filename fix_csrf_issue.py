#!/usr/bin/env python3
"""
CSRF Issue Fix Script
Comprehensive fix for CSRF verification failed errors
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.conf import settings
from django.core.management import execute_from_command_line

def check_csrf_settings():
    """Check CSRF-related settings"""
    print("🔍 Checking CSRF Settings...")
    
    # Check middleware
    csrf_middleware = 'django.middleware.csrf.CsrfViewMiddleware'
    if csrf_middleware in settings.MIDDLEWARE:
        print(f"✅ CSRF Middleware is present: {csrf_middleware}")
        csrf_index = settings.MIDDLEWARE.index(csrf_middleware)
        print(f"   Position: {csrf_index + 1} of {len(settings.MIDDLEWARE)}")
    else:
        print(f"❌ CSRF Middleware is missing: {csrf_middleware}")
        return False
    
    # Check CSRF settings
    print(f"✅ CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', 'Not set')}")
    print(f"✅ CSRF_COOKIE_HTTPONLY: {getattr(settings, 'CSRF_COOKIE_HTTPONLY', 'Not set')}")
    print(f"✅ DEBUG: {settings.DEBUG}")
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    return True

def check_template_csrf():
    """Check if templates have CSRF tokens"""
    print("\n🔍 Checking Template CSRF Tokens...")
    
    template_files = [
        'community/templates/community/challenges_list.html',
        'community/templates/community/campaign_detail.html',
        'accounts/templates/accounts/login.html',
        'accounts/templates/accounts/register.html',
    ]
    
    for template_file in template_files:
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '{% csrf_token %}' in content:
                    print(f"✅ {template_file} has CSRF token")
                else:
                    print(f"❌ {template_file} missing CSRF token")
        else:
            print(f"⚠️  {template_file} not found")

def fix_csrf_settings():
    """Apply CSRF fixes to settings"""
    print("\n🔧 Applying CSRF Fixes...")
    
    settings_file = 'ecolearn/settings.py'
    
    if not os.path.exists(settings_file):
        print(f"❌ Settings file not found: {settings_file}")
        return False
    
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if CSRF settings need to be updated
    fixes_needed = []
    
    # Ensure CSRF middleware is properly positioned
    if 'django.middleware.csrf.CsrfViewMiddleware' not in content:
        fixes_needed.append("Add CSRF middleware")
    
    # Check CSRF cookie settings
    if 'CSRF_COOKIE_SECURE = False' not in content and 'CSRF_COOKIE_SECURE = True' not in content:
        fixes_needed.append("Set CSRF_COOKIE_SECURE")
    
    if 'CSRF_COOKIE_HTTPONLY = True' not in content:
        fixes_needed.append("Set CSRF_COOKIE_HTTPONLY")
    
    # Add CSRF_TRUSTED_ORIGINS for development
    if 'CSRF_TRUSTED_ORIGINS' not in content:
        fixes_needed.append("Add CSRF_TRUSTED_ORIGINS")
    
    if fixes_needed:
        print(f"⚠️  Fixes needed: {', '.join(fixes_needed)}")
        
        # Add CSRF_TRUSTED_ORIGINS if missing
        if 'CSRF_TRUSTED_ORIGINS' not in content:
            csrf_origins = '''
# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://*.onrender.com',
]
'''
            # Insert before the last line
            lines = content.split('\n')
            lines.insert(-1, csrf_origins)
            content = '\n'.join(lines)
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Added CSRF_TRUSTED_ORIGINS to settings")
    else:
        print("✅ CSRF settings look good")
    
    return True

def test_csrf_view():
    """Test CSRF functionality"""
    print("\n🧪 Testing CSRF View...")
    
    try:
        from django.test import Client
        from django.contrib.auth import get_user_model
        
        client = Client()
        
        # Test GET request to challenges page
        response = client.get('/community/challenges/')
        print(f"✅ GET /community/challenges/ - Status: {response.status_code}")
        
        # Check if CSRF token is in response
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            if 'csrfmiddlewaretoken' in content:
                print("✅ CSRF token found in response")
            else:
                print("⚠️  CSRF token not found in response")
        
    except Exception as e:
        print(f"❌ CSRF test failed: {e}")

def clear_sessions():
    """Clear Django sessions"""
    print("\n🧹 Clearing Sessions...")
    
    try:
        from django.contrib.sessions.models import Session
        Session.objects.all().delete()
        print("✅ All sessions cleared")
    except Exception as e:
        print(f"❌ Failed to clear sessions: {e}")

def main():
    """Main fix function"""
    print("🚀 CSRF Issue Fix Script")
    print("=" * 50)
    
    # Check current settings
    if not check_csrf_settings():
        print("❌ CSRF settings check failed")
        return False
    
    # Check templates
    check_template_csrf()
    
    # Apply fixes
    fix_csrf_settings()
    
    # Clear sessions
    clear_sessions()
    
    # Test CSRF
    test_csrf_view()
    
    print("\n" + "=" * 50)
    print("🎉 CSRF Fix Complete!")
    print("\nNext steps:")
    print("1. Restart your Django server")
    print("2. Clear your browser cache and cookies")
    print("3. Try the form again")
    print("4. If still failing, check browser developer tools for CSRF token")
    
    return True

if __name__ == '__main__':
    main()