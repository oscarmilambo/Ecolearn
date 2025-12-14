#!/usr/bin/env python
"""
Check Django settings for deprecation warnings
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    print("🔍 Running Django system check...")
    print("=" * 50)
    try:
        execute_from_command_line(['manage.py', 'check'])
        print("\n✅ System check completed!")
    except Exception as e:
        print(f"❌ Error: {e}")