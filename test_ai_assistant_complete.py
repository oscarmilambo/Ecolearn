#!/usr/bin/env python
"""
Complete AI Assistant Test - Run this after updating the API key
"""
import os
import django
from decouple import config

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

def test_complete_ai_assistant():
    """Test the complete AI assistant functionality"""
    print("🤖 Testing Complete AI Assistant Setup...")
    print("=" * 60)
    
    # Test 1: Check API Key
    print("1. Checking API Key...")
    api_key = config('GEMINI_API_KEY', default='')
    if not api_key or api_key == 'your-new-api-key-here':
        print("❌ API Key not set. Please update GEMINI_API_KEY in .env file")
        print("   Go to: https://makersuite.google.com/app/apikey")
        return False
    else:
        print(f"✅ API Key present (length: {len(api_key)})")
    
    # Test 2: Check Package Installation
    print("\n2. Checking Google Generative AI package...")
    try:
        import google.generativeai as genai
        print("✅ google-generativeai package installed")
    except ImportError:
        print("❌ google-generativeai package not installed")
        print("   Run: pip install google-generativeai")
        return False
    
    # Test 3: Test API Connection
    print("\n3. Testing API Connection...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Say 'Hello from EcoLearn AI!'")
        print(f"✅ API Connection successful: {response.text}")
    except Exception as e:
        print(f"❌ API Connection failed: {e}")
        print("   Check if your API key is valid")
        return False
    
    # Test 4: Check Django Models
    print("\n4. Checking Django Models...")
    try:
        from ai_assistant.models import ChatSession, ChatMessage, AssistantFeedback
        print("✅ AI Assistant models imported successfully")
    except ImportError as e:
        print(f"❌ Model import failed: {e}")
        return False
    
    # Test 5: Check URLs
    print("\n5. Checking URL Configuration...")
    try:
        from django.urls import reverse
        chat_url = reverse('ai_assistant:chat')
        print(f"✅ AI Assistant URLs configured: {chat_url}")
    except Exception as e:
        print(f"❌ URL configuration error: {e}")
        return False
    
    # Test 6: Check Template
    print("\n6. Checking Template...")
    import os
    template_path = 'ai_assistant/templates/ai_assistant/chat.html'
    if os.path.exists(template_path):
        print("✅ Chat template exists")
    else:
        print("❌ Chat template missing")
        return False
    
    # Test 7: Check Views
    print("\n7. Checking Views...")
    try:
        from ai_assistant.views import chat_interface, send_message
        print("✅ AI Assistant views imported successfully")
    except ImportError as e:
        print(f"❌ Views import failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED! AI Assistant is ready to use!")
    print("\n📋 Next Steps:")
    print("1. Start your Django server: python manage.py runserver")
    print("2. Visit: http://127.0.0.1:8000/ai-assistant/")
    print("3. Or click 'AI Assistant' in the navbar")
    print("\n🎯 Features Available:")
    print("- Real-time chat with Gemini AI")
    print("- Navigation help")
    print("- Environmental tips")
    print("- Feature explanations")
    print("- Multi-language support")
    
    return True

if __name__ == "__main__":
    success = test_complete_ai_assistant()
    
    if not success:
        print("\n❌ Setup incomplete. Please fix the issues above.")
    else:
        print("\n🚀 Ready to chat with your AI Assistant!")