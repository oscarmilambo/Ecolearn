#!/usr/bin/env python
"""
Test AI Assistant endpoint directly
"""
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def test_ai_endpoint():
    print("=== TESTING AI ASSISTANT ENDPOINT ===")
    
    # Create test client
    client = Client()
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        username='ai_test_user',
        defaults={'email': 'aitest@example.com'}
    )
    
    # Login the user
    client.force_login(user)
    print(f"✅ Logged in as: {user.username}")
    
    # Test 1: Access chat interface
    try:
        response = client.get('/ai-assistant/')
        print(f"Chat interface status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Chat interface accessible")
        else:
            print(f"❌ Chat interface failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat interface error: {e}")
    
    # Test 2: Send a message
    try:
        message_data = {
            'message': 'Hello, can you help me?',
            'session_id': None
        }
        
        response = client.post(
            '/ai-assistant/send/',
            data=json.dumps(message_data),
            content_type='application/json'
        )
        
        print(f"Send message status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Message sent successfully!")
                print(f"AI Response: {data['assistant_message']['content'][:100]}...")
            else:
                print(f"❌ Message failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.content.decode()[:200]}...")
            
    except Exception as e:
        print(f"❌ Send message error: {e}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_ai_endpoint()