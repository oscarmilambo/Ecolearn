#!/usr/bin/env python3
"""
Direct Form Test - No Django setup
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')

import django
django.setup()

# Clear any cached modules
if 'accounts.forms' in sys.modules:
    del sys.modules['accounts.forms']

# Import fresh
from accounts.forms import CustomUserCreationForm

def test_form_direct():
    """Test form directly"""
    print("🔍 Direct Form Test")
    print("=" * 30)
    
    # Create form instance
    form = CustomUserCreationForm()
    
    print(f"Form class: {form.__class__}")
    print(f"Form fields: {list(form.fields.keys())}")
    
    # Check each field
    for field_name, field in form.fields.items():
        print(f"  {field_name}: {type(field).__name__} (required: {field.required})")
    
    # Test with data
    test_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'gender': 'male',
        'email': 'test@example.com',
        'contact_method': '260971234567',
        'password': 'testpass123'
    }
    
    form_with_data = CustomUserCreationForm(data=test_data)
    
    print(f"\nForm with data is valid: {form_with_data.is_valid()}")
    
    if not form_with_data.is_valid():
        print(f"Errors: {form_with_data.errors}")
    else:
        print(f"Cleaned data: {form_with_data.cleaned_data}")

if __name__ == '__main__':
    test_form_direct()