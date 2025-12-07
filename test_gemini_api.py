#!/usr/bin/env python3
"""
Test script to verify Gemini API key is working
Run this to check if your API key is valid
"""

import os
import sys
from decouple import config

# Add Django project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gemini_api():
    """Test the Gemini API key"""
    try:
        # Load API key from .env
        api_key = config('GEMINI_API_KEY', default='')
        
        if not api_key:
            print("❌ ERROR: GEMINI_API_KEY not found in .env file")
            return False
            
        print(f"✅ API Key loaded: {api_key[:10]}...{api_key[-4:]}")
        
        # Try to import and configure Gemini
        try:
            import google.generativeai as genai
            print("✅ google.generativeai imported successfully")
        except ImportError:
            print("❌ ERROR: google-generativeai not installed")
            print("Run: pip install google-generativeai")
            return False
        
        # Configure with API key
        genai.configure(api_key=api_key)
        print("✅ Gemini configured with API key")
        
        # Test with a simple request
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Gemini model initialized")
        
        # Send test message
        response = model.generate_content("Say 'Hello from EcoLearn AI!' in one sentence.")
        print(f"✅ API Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🤖 Testing Gemini AI API Configuration...")
    print("=" * 50)
    
    success = test_gemini_api()
    
    print("=" * 50)
    if success:
        print("🎉 SUCCESS: Gemini API is working correctly!")
        print("Your AI Assistant should now work properly.")
    else:
        print("💥 FAILED: Please check your API key and configuration.")
        print("\nTroubleshooting:")
        print("1. Verify your API key at: https://makersuite.google.com/app/apikey")
        print("2. Make sure it's correctly set in your .env file")
        print("3. Install required package: pip install google-generativeai")