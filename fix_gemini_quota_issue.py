#!/usr/bin/env python
"""
Fix Gemini API quota issue by finding working models
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.conf import settings
import google.generativeai as genai

def find_working_model():
    print("=== FINDING WORKING GEMINI MODEL ===")
    
    api_key = settings.GEMINI_API_KEY
    genai.configure(api_key=api_key)
    
    # List of models to try (from most basic to advanced)
    models_to_try = [
        'gemini-1.5-flash-8b',  # Smallest, cheapest
        'gemini-1.5-flash',     # Standard
        'gemini-1.5-pro',       # More capable
        'gemini-2.5-flash',     # Latest flash
    ]
    
    for model_name in models_to_try:
        try:
            print(f"\n🔍 Testing model: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            # Try a very simple request
            response = model.generate_content("Hi")
            
            if response and response.text:
                print(f"✅ SUCCESS! Model {model_name} is working")
                print(f"Response: {response.text}")
                return model_name
            else:
                print(f"❌ Model {model_name} returned empty response")
                
        except Exception as e:
            print(f"❌ Model {model_name} failed: {str(e)[:100]}...")
    
    print("\n💥 No working models found")
    return None

if __name__ == "__main__":
    working_model = find_working_model()
    if working_model:
        print(f"\n🎉 Use this model: {working_model}")
    else:
        print("\n⚠️  All models failed - quota may be exhausted")