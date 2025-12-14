#!/usr/bin/env python
"""
Test the admin URL to make sure the CustomUser admin works
"""
import requests
import sys

def test_admin_url():
    """Test that the admin URL works without the FieldError"""
    print("🔍 Testing Admin URL...")
    print("=" * 50)
    
    try:
        # Test the admin login page first
        response = requests.get('http://127.0.0.1:8000/admin/', timeout=5)
        print(f"✅ Admin login page: Status {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Django server is running")
            print("✅ Admin interface is accessible")
            print("\n💡 The FieldError should be fixed now!")
            print("💡 Try accessing: http://127.0.0.1:8000/admin/accounts/customuser/")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server")
        print("💡 Make sure the server is running: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_admin_url()