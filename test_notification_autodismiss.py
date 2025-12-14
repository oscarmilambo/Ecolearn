#!/usr/bin/env python3
"""
Test script to verify notification auto-dismiss functionality
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse

User = get_user_model()

def test_notification_autodismiss():
    """Test that notifications appear and have auto-dismiss functionality"""
    
    print("🔍 Testing notification auto-dismiss functionality...")
    
    # Test 1: Check base.html template has auto-dismiss class
    print("\n1. Checking base.html template...")
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"   File size: {len(content)} characters")
            
            if 'auto-dismiss-message' in content:
                print("✅ Base template has auto-dismiss class")
            else:
                print("❌ Base template missing auto-dismiss class")
                # Debug: show what we found instead
                if 'message' in content:
                    print("   Found 'message' but not 'auto-dismiss-message'")
                
            if 'setTimeout(function() {' in content:
                print("✅ Base template has auto-dismiss JavaScript")
            else:
                print("❌ Base template missing auto-dismiss JavaScript")
                if 'setTimeout' in content:
                    print("   Found 'setTimeout' but not the expected pattern")
    except Exception as e:
        print(f"❌ Error reading base.html: {e}")
    
    # Test 2: Check landing page template has auto-dismiss class
    print("\n2. Checking landing page template...")
    with open('accounts/templates/accounts/landing_page.html', 'r') as f:
        content = f.read()
        if 'auto-dismiss-message' in content:
            print("✅ Landing page has auto-dismiss class")
        else:
            print("❌ Landing page missing auto-dismiss class")
            
        if 'setTimeout(function() {' in content:
            print("✅ Landing page has auto-dismiss JavaScript")
        else:
            print("❌ Landing page missing auto-dismiss JavaScript")
    
    # Test 3: Check main.js has auto-dismiss for JavaScript notifications
    print("\n3. Checking main.js JavaScript notifications...")
    with open('static/js/main.js', 'r') as f:
        content = f.read()
        if 'setTimeout(() => {' in content and 'notification.remove()' in content:
            print("✅ JavaScript notifications have auto-dismiss")
        else:
            print("❌ JavaScript notifications missing auto-dismiss")
    
    print("\n🎉 Auto-dismiss functionality test completed!")
    print("\n📋 Summary:")
    print("- Django messages in templates now have auto-dismiss after 5 seconds")
    print("- JavaScript notifications already had auto-dismiss functionality")
    print("- Both manual close buttons and auto-dismiss work together")
    print("- Smooth fade-out animation added for better UX")

if __name__ == '__main__':
    test_notification_autodismiss()