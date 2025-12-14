#!/usr/bin/env python
"""
Debug settings to see what's happening
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.conf import settings

def debug_settings():
    """Debug the settings"""
    print("🔍 Debugging Settings...")
    print("=" * 50)
    
    # Check all ACCOUNT_ settings
    account_settings = [attr for attr in dir(settings) if attr.startswith('ACCOUNT_')]
    print(f"All ACCOUNT_ settings: {account_settings}")
    
    # Check specific settings
    settings_to_check = [
        'ACCOUNT_LOGIN_METHODS',
        'ACCOUNT_SIGNUP_FIELDS', 
        'ACCOUNT_RATE_LIMITS',
        'ACCOUNT_AUTHENTICATION_METHOD',
        'ACCOUNT_EMAIL_REQUIRED',
        'ACCOUNT_USERNAME_REQUIRED'
    ]
    
    for setting in settings_to_check:
        if hasattr(settings, setting):
            value = getattr(settings, setting)
            print(f"✅ {setting}: {value}")
        else:
            print(f"❌ {setting}: Not found")

if __name__ == "__main__":
    debug_settings()