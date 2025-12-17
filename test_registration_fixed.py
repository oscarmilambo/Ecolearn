#!/usr/bin/env python3
"""
Test Registration Process - Fixed Version
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.test import Client
from accounts.models import CustomUser
from accounts.forms import CustomUserCreationForm

def test_registration_process():
    """Test the complete registration process"""
    print("🔍 Testing Registration Process - Fixed")
    print("=" * 50)
    
    # Test 1: Form validation
    print("\n1. Testing form validation...")
    
    form_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'gender': 'male',
        'email': 'john.doe@example.com',
        'contact_method': '260971234567',
        'password': 'testpass123'
    }
    
    form = CustomUserCreationForm(data=form_data)
    
    if form.is_valid():
        print("   ✅ Form validation passed")
        print(f"   Cleaned data: {form.cleaned_data}")
    else:
        print("   ❌ Form validation failed")
        print(f"   Errors: {form.errors}")
        return False
    
    # Test 2: POST request to registration
    print("\n2. Testing POST request...")
    
    client = Client()
    
    # Clear any existing user with this data
    CustomUser.objects.filter(email='john.doe@example.com').delete()
    CustomUser.objects.filter(phone_number='260971234567').delete()
    
    response = client.post('/accounts/register/', data=form_data)
    
    print(f"   POST Status: {response.status_code}")
    
    if response.status_code == 302:
        print("   ✅ Registration successful (redirect)")
        print(f"   Redirect location: {response.get('Location', 'Not specified')}")
        
        # Check if user was created
        user = CustomUser.objects.filter(email='john.doe@example.com').first()
        if user:
            print(f"   ✅ User created: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Phone: {user.phone_number}")
            print(f"   First name: {user.first_name}")
            print(f"   Last name: {user.last_name}")
        else:
            print("   ❌ User not found in database")
            
    elif response.status_code == 200:
        print("   ⚠️  Registration form returned (may have errors)")
        content = response.content.decode('utf-8')
        if 'error' in content.lower():
            print("   ❌ Form contains errors")
        else:
            print("   ✅ Form processed successfully")
    else:
        print(f"   ❌ Unexpected status: {response.status_code}")
    
    # Test 3: Test with email as contact method
    print("\n3. Testing with email as contact method...")
    
    email_form_data = {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'gender': 'female',
        'email': 'jane.smith@example.com',
        'contact_method': 'jane.contact@example.com',  # Email as contact
        'password': 'testpass456'
    }
    
    # Clear any existing user
    CustomUser.objects.filter(email__in=['jane.smith@example.com', 'jane.contact@example.com']).delete()
    
    email_response = client.post('/accounts/register/', data=email_form_data)
    
    print(f"   Email contact POST Status: {email_response.status_code}")
    
    if email_response.status_code == 302:
        print("   ✅ Email contact registration successful")
        
        user = CustomUser.objects.filter(email='jane.smith@example.com').first()
        if user:
            print(f"   ✅ User created with email contact: {user.username}")
        else:
            print("   ❌ User not found")
    else:
        print(f"   ⚠️  Email contact registration status: {email_response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 Registration Process Test Complete!")

if __name__ == '__main__':
    test_registration_process()