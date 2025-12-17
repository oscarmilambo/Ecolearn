#!/usr/bin/env python
"""
Test Gemini AI connection
"""
import os
import django
from decouple import config

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

def test_gemini_connection():
    """Test if Gemini AI is working properly"""
    try:
        import google.generativeai as genai
        
        # Get API key
        api_key = config('GEMINI_API_KEY', default='')
        print(f"API Key present: {'Yes' if api_key else 'No'}")
        print(f"API Key length: {len(api_key) if api_key else 0}")
        
        if not api_key:
            print("❌ ERROR: GEMINI_API_KEY not found in .env file")
            return False
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        print("✅ Gemini configured successfully")
        
        # Test model
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ Model initialized successfully")
        
        # Test simple query
        response = model.generate_content("Hello, can you respond with 'AI is working!'?")
        print(f"✅ Test response: {response.text}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Testing Gemini AI Connection...")
    print("=" * 50)
    
    success = test_gemini_connection()
    
    print("=" * 50)
    if success:
        print("✅ Gemini AI is working correctly!")
    else:
        print("❌ Gemini AI connection failed!")