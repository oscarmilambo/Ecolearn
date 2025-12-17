#!/usr/bin/env python
"""
Complete test of Gemini AI functionality
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.conf import settings

def test_gemini_complete():
    print("=== COMPLETE GEMINI AI TEST ===")
    
    # Test 1: Check API key
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if api_key:
        print(f"✅ API Key configured: {api_key[:10]}...")
    else:
        print("❌ API Key not configured")
        return False
    
    # Test 2: Try importing the package
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import google.generativeai: {e}")
        print("💡 Try: pip install google-generativeai")
        return False
    
    # Test 3: Configure the API
    try:
        genai.configure(api_key=api_key)
        print("✅ Gemini API configured successfully")
    except Exception as e:
        print(f"❌ Failed to configure Gemini API: {e}")
        return False
    
    # Test 4: List available models
    try:
        models = list(genai.list_models())
        print(f"✅ Found {len(models)} available models")
        
        # Find the best model to use
        gemini_models = [m for m in models if 'gemini' in m.name.lower()]
        if gemini_models:
            print("Available Gemini models:")
            for model in gemini_models[:3]:  # Show first 3
                print(f"  - {model.name}")
        
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
        return False
    
    # Test 5: Try a simple API call
    try:
        # Use the latest available model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        response = model.generate_content("Hello! Can you help me with environmental questions?")
        
        if response and response.text:
            print("✅ API call successful!")
            print(f"Response: {response.text[:100]}...")
            return True
        else:
            print("❌ API call returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ API call failed: {e}")
        
        # Try with a different model
        try:
            print("🔄 Trying with gemini-1.5-flash...")
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Hello! Can you help me with environmental questions?")
            
            if response and response.text:
                print("✅ API call successful with gemini-1.5-flash!")
                print(f"Response: {response.text[:100]}...")
                return True
            else:
                print("❌ API call returned empty response")
                return False
                
        except Exception as e2:
            print(f"❌ Second API call also failed: {e2}")
            return False

if __name__ == "__main__":
    success = test_gemini_complete()
    if success:
        print("\n🎉 Gemini AI is working correctly!")
    else:
        print("\n💥 Gemini AI setup needs fixing")