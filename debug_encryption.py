#!/usr/bin/env python
"""
Debug script to check encryption key handling
"""
import os
import sys
import django
from cryptography.fernet import Fernet

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.conf import settings

def debug_encryption():
    print("🔍 Debugging Encryption Key Issue")
    print("=" * 50)
    
    # Check environment variable
    env_key = os.environ.get('ENCRYPTION_KEY')
    print(f"Environment ENCRYPTION_KEY: {env_key}")
    
    # Check Django settings
    settings_key = getattr(settings, 'ENCRYPTION_KEY', None)
    print(f"Django settings ENCRYPTION_KEY: {settings_key}")
    
    # Test key validity
    if env_key:
        try:
            test_cipher = Fernet(env_key.encode())
            print("✅ Environment key is valid for Fernet")
        except Exception as e:
            print(f"❌ Environment key error: {e}")
    
    if settings_key:
        try:
            test_cipher = Fernet(settings_key.encode())
            print("✅ Settings key is valid for Fernet")
        except Exception as e:
            print(f"❌ Settings key error: {e}")
    
    # Generate a new valid key
    new_key = Fernet.generate_key().decode()
    print(f"\n🔑 New valid key: {new_key}")
    
    # Test the new key
    try:
        test_cipher = Fernet(new_key.encode())
        test_data = b"Hello, World!"
        encrypted = test_cipher.encrypt(test_data)
        decrypted = test_cipher.decrypt(encrypted)
        print("✅ New key encryption/decryption test passed")
    except Exception as e:
        print(f"❌ New key test failed: {e}")

if __name__ == "__main__":
    debug_encryption()