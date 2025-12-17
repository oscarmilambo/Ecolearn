#!/usr/bin/env python
"""
Debug AI Assistant Issues
"""
import requests
import json

def test_ai_assistant_debug():
    """Test AI Assistant endpoints directly"""
    print("🔍 Debugging AI Assistant...")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Check if AI Assistant page loads
    print("1. Testing AI Assistant Page...")
    try:
        response = requests.get(f"{base_url}/ai-assistant/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Page loads successfully")
            # Check for JavaScript errors in the HTML
            if "currentSessionId" in response.text:
                print("   ✅ JavaScript variables found")
            else:
                print("   ❌ JavaScript variables missing")
        elif response.status_code == 302:
            print("   ⚠️ Redirected (need to login)")
            print(f"   Redirect to: {response.headers.get('Location', 'Unknown')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Check if we can access the send endpoint (will fail without login)
    print("\n2. Testing Send Message Endpoint...")
    try:
        response = requests.post(f"{base_url}/ai-assistant/send/", 
                               json={"message": "test"}, 
                               timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 403:
            print("   ✅ CSRF protection working (expected)")
        elif response.status_code == 302:
            print("   ✅ Login required (expected)")
        else:
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Check new session endpoint
    print("\n3. Testing New Session Endpoint...")
    try:
        response = requests.post(f"{base_url}/ai-assistant/session/new/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [302, 403]:
            print("   ✅ Authentication/CSRF protection working")
        else:
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Make sure you're logged in")
    print("2. Check browser console for JavaScript errors")
    print("3. Try clicking 'New Chat' button")
    print("4. Try typing a message and pressing Enter")

if __name__ == "__main__":
    test_ai_assistant_debug()