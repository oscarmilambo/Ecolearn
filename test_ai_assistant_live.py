#!/usr/bin/env python
"""
Test AI Assistant Live - Test the actual web interface
"""
import requests
import json

def test_ai_assistant_live():
    """Test the AI Assistant through the web interface"""
    print("🤖 Testing AI Assistant Live Interface...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Check if AI Assistant page loads
    print("1. Testing AI Assistant Page Access...")
    try:
        response = requests.get(f"{base_url}/ai-assistant/", timeout=10)
        if response.status_code == 200:
            print("✅ AI Assistant page loads successfully")
            if "EcoLearn AI Assistant" in response.text:
                print("✅ Page contains correct title")
            else:
                print("⚠️ Page loaded but title not found")
        elif response.status_code == 302:
            print("⚠️ Redirected (probably need to login first)")
            print(f"   Redirect location: {response.headers.get('Location', 'Unknown')}")
        else:
            print(f"❌ Page failed to load: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: Check if login page works (since AI Assistant requires login)
    print("\n2. Testing Login Page...")
    try:
        response = requests.get(f"{base_url}/accounts/login/", timeout=10)
        if response.status_code == 200:
            print("✅ Login page accessible")
        else:
            print(f"❌ Login page error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Login page error: {e}")
    
    # Test 3: Check if main site is working
    print("\n3. Testing Main Site...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Main site accessible")
            if "EcoLearn" in response.text:
                print("✅ Site contains EcoLearn branding")
        else:
            print(f"❌ Main site error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Main site error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("1. Open your browser")
    print("2. Go to: http://127.0.0.1:8000/")
    print("3. Login or register an account")
    print("4. Click 'AI Assistant' in the navbar")
    print("5. Start chatting!")
    
    print("\n💡 Test Questions to Try:")
    print("- 'How do I report illegal dumping?'")
    print("- 'What learning modules are available?'")
    print("- 'Help me navigate the platform'")
    print("- 'Tell me about waste management'")
    
    return True

if __name__ == "__main__":
    test_ai_assistant_live()