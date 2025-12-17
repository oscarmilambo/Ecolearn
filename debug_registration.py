#!/usr/bin/env python3
"""
Debug Registration Form Issue
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from accounts.forms import CustomUserCreationForm
from django.test import Client, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage

def test_registration_form():
    """Test the registration form with sample data"""
    print("🔍 Testing Registration Form")
    print("=" * 40)
    
    # Test 1: Test form with valid data
    print("\n1. Testing form with valid data...")
    
    form_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'gender': 'male',
        'phone_number': '260971234567',
        'password': 'testpass123'
    }
    
    form = CustomUserCreationForm(data=form_data)
    
    print(f"   Form is valid: {form.is_valid()}")
    
    if form.is_valid():
        print("   ✅ Form validation passed")
        print(f"   Cleaned data keys: {list(form.cleaned_data.keys())}")
        
        for key, value in form.cleaned_data.items():
            print(f"   {key}: {value}")
            
    else:
        print("   ❌ Form validation failed")
        print(f"   Form errors: {form.errors}")
        
        # Check which fields are missing
        for field_name in ['first_name', 'last_name', 'gender', 'phone_number', 'password']:
            if field_name in form.errors:
                print(f"   Error in {field_name}: {form.errors[field_name]}")
    
    # Test 2: Test POST request simulation
    print("\n2. Testing POST request simulation...")
    
    client = Client()
    
    # Test POST to registration
    response = client.post('/accounts/register/', data=form_data)
    
    print(f"   POST Status: {response.status_code}")
    
    if response.status_code == 200:
        # Check if there are form errors in the response
        content = response.content.decode('utf-8')
        if 'error' in content.lower():
            print("   ⚠️  Response contains errors")
        else:
            print("   ✅ POST request processed")
    elif response.status_code == 302:
        print("   ✅ POST successful (redirect)")
        print(f"   Redirect location: {response.get('Location', 'Not specified')}")
    else:
        print(f"   ❌ Unexpected status: {response.status_code}")
    
    # Test 3: Check form field names
    print("\n3. Checking form field names...")
    
    form = CustomUserCreationForm()
    
    print(f"   Form fields: {list(form.fields.keys())}")
    
    for field_name, field in form.fields.items():
        print(f"   {field_name}: {type(field).__name__} (required: {field.required})")
    
    # Test 4: Test with missing phone_number
    print("\n4. Testing with missing phone_number...")
    
    incomplete_data = {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'gender': 'female',
        'password': 'testpass456'
        # phone_number missing
    }
    
    incomplete_form = CustomUserCreationForm(data=incomplete_data)
    
    print(f"   Incomplete form is valid: {incomplete_form.is_valid()}")
    
    if not incomplete_form.is_valid():
        print(f"   Expected errors: {incomplete_form.errors}")
        
        if 'phone_number' in incomplete_form.errors:
            print("   ✅ phone_number error detected as expected")
        else:
            print("   ❌ phone_number error not detected")
    
    print("\n" + "=" * 40)
    print("🎉 Registration Form Debug Complete!")

if __name__ == '__main__':
    test_registration_form()