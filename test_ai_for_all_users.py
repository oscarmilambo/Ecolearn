#!/usr/bin/env python
"""
Test AI Assistant for all user types - FINAL VERIFICATION
"""
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_all_user_types():
    print("🚀 TESTING AI ASSISTANT FOR ALL USER TYPES")
    
    # Test 1: Regular User
    print("\n1. TESTING REGULAR USER")
    client1 = Client()
    
    # Create regular user
    regular_user, created = User.objects.get_or_create(
        username='regular_user_test',
        defaults={'email': 'regular@test.com', 'role': 'user'}
    )
    client1.force_login(regular_user)
    
    # Test message
    response = client1.post('/ai-assistant/send/', 
        data=json.dumps({'message': 'Hello AI!', 'session_id': None}),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Regular user: AI working!")
            print(f"   Response: {data['assistant_message']['content'][:50]}...")
        else:
            print("❌ Regular user: Failed")
    else:
        print(f"❌ Regular user: HTTP {response.status_code}")
    
    # Test 2: Admin User
    print("\n2. TESTING ADMIN USER")
    client2 = Client()
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin_user_test',
        defaults={'email': 'admin@test.com', 'role': 'admin', 'is_staff': True}
    )
    client2.force_login(admin_user)
    
    # Test message
    response = client2.post('/ai-assistant/send/', 
        data=json.dumps({'message': 'How can I help users?', 'session_id': None}),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Admin user: AI working!")
            print(f"   Response: {data['assistant_message']['content'][:50]}...")
        else:
            print("❌ Admin user: Failed")
    else:
        print(f"❌ Admin user: HTTP {response.status_code}")
    
    # Test 3: Different Question Types
    print("\n3. TESTING DIFFERENT QUESTIONS")
    
    test_questions = [
        "Tell me about recycling",
        "How do I report dumping?", 
        "What learning modules are available?",
        "How can I get involved in my community?",
        "Random question about something else"
    ]
    
    for i, question in enumerate(test_questions, 1):
        response = client1.post('/ai-assistant/send/', 
            data=json.dumps({'message': question, 'session_id': None}),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Question {i}: Working")
            else:
                print(f"❌ Question {i}: Failed")
        else:
            print(f"❌ Question {i}: HTTP Error")
    
    print("\n🎉 AI ASSISTANT TESTING COMPLETE!")
    print("The AI Assistant is ready for your presentation!")

if __name__ == "__main__":
    test_all_user_types()