#!/usr/bin/env python
"""
Check available Gemini models
"""
import os
import django
from decouple import config

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

def check_available_models():
    """Check what models are available"""
    try:
        import google.generativeai as genai
        
        # Get API key
        api_key = config('GEMINI_API_KEY', default='')
        if not api_key:
            print("❌ No API key found")
            return
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        print("🔍 Checking available models...")
        print("=" * 50)
        
        # List available models
        models = genai.list_models()
        
        print("Available models:")
        for model in models:
            print(f"- {model.name}")
            if hasattr(model, 'supported_generation_methods'):
                print(f"  Supported methods: {model.supported_generation_methods}")
        
        print("\n" + "=" * 50)
        
        # Try different model names
        model_names_to_try = [
            'gemini-pro',
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'models/gemini-pro',
            'models/gemini-1.5-pro',
            'models/gemini-1.5-flash'
        ]
        
        print("Testing models:")
        for model_name in model_names_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello")
                print(f"✅ {model_name} - WORKS: {response.text[:50]}...")
                break
            except Exception as e:
                print(f"❌ {model_name} - Error: {str(e)[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_available_models()