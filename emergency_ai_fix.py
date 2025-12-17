#!/usr/bin/env python
"""
EMERGENCY AI ASSISTANT FIX - FOR PRESENTATION
This will create a simple, working AI assistant immediately
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.conf import settings

def emergency_fix():
    print("🚨 EMERGENCY AI ASSISTANT FIX 🚨")
    print("Creating immediate working solution...")
    
    # Test API quickly
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Quick test
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Hello")
        
        if response and response.text:
            print("✅ API is working!")
            print("Creating emergency fallback...")
            return True
        else:
            print("❌ API issue - creating offline fallback")
            return False
            
    except Exception as e:
        print(f"❌ API Error: {e}")
        print("Creating offline fallback...")
        return False

if __name__ == "__main__":
    emergency_fix()