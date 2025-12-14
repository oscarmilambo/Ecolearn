#!/usr/bin/env python3
"""
Test script to verify welcome message auto-dismiss functionality
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

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def test_welcome_message_autodismiss():
    """Test that welcome message appears and has auto-dismiss functionality"""
    
    print("🔍 Testing welcome message auto-dismiss functionality...")
    
    # Create test client
    client = Client()
    
    try:
        # Try to get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser_welcome',
            defaults={
                'email': 'test_welcome@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            print("✅ Created test user")
        else:
            print("✅ Using existing test user")
        
        # Test login to trigger welcome message
        print("\n🔐 Testing login process...")
        
        # First, get the login page
        login_url = reverse('accounts:login')
        response = client.get(login_url)
        print(f"   Login page status: {response.status_code}")
        
        # Perform login
        login_data = {
            'username': 'testuser_welcome',
            'password': 'testpass123'
        }
        
        response = client.post(login_url, login_data, follow=True)
        print(f"   Login response status: {response.status_code}")
        
        # Check if redirected to dashboard
        if response.status_code == 200:
            print("✅ Login successful")
            
            # Check if welcome message is in the response
            content = response.content.decode('utf-8')
            
            if 'Welcome back' in content:
                print("✅ Welcome message found in response")
                
                # Check if auto-dismiss functionality is present
                if 'auto-dismiss-message' in content:
                    print("✅ Auto-dismiss class found in HTML")
                else:
                    print("❌ Auto-dismiss class NOT found in HTML")
                
                if 'querySelectorAll(\'.auto-dismiss-message\')' in content:
                    print("✅ Auto-dismiss JavaScript found in HTML")
                else:
                    print("❌ Auto-dismiss JavaScript NOT found in HTML")
                    
            else:
                print("❌ Welcome message NOT found in response")
                
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    print("\n📋 Summary:")
    print("- Welcome message should appear when user logs in")
    print("- Message should have 'auto-dismiss-message' CSS class")
    print("- JavaScript should automatically remove message after 5 seconds")
    print("- User can also manually close message with X button")

if __name__ == '__main__':
    test_welcome_message_autodismiss()