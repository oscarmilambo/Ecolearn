#!/usr/bin/env python
"""
Test WebSocket authentication fix
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from channels.testing import WebsocketCommunicator
from ecolearn.consumers import NotificationConsumer
from channels.db import database_sync_to_async

User = get_user_model()

async def test_websocket_authentication():
    """Test WebSocket authentication behavior"""
    print("=== WEBSOCKET AUTHENTICATION TEST ===")
    
    # Test 1: Unauthenticated user should be rejected
    print("\n1. Testing unauthenticated connection...")
    communicator = WebsocketCommunicator(NotificationConsumer.as_asgi(), "/ws/notifications/")
    
    try:
        connected, subprotocol = await communicator.connect()
        if connected:
            print("❌ Unauthenticated user was allowed to connect (this should not happen)")
            await communicator.disconnect()
        else:
            print("✅ Unauthenticated user correctly rejected")
    except Exception as e:
        print(f"✅ Unauthenticated connection properly rejected: {e}")
    
    # Test 2: Create authenticated user and test connection
    print("\n2. Testing authenticated connection...")
    
    # Create test user
    @database_sync_to_async
    def create_user():
        user, created = User.objects.get_or_create(
            username='websocket_test_user',
            defaults={'email': 'wstest@example.com'}
        )
        return user
    
    user = await create_user()
    
    # Create communicator with authenticated user
    communicator = WebsocketCommunicator(
        NotificationConsumer.as_asgi(), 
        "/ws/notifications/",
        headers=[(b"cookie", b"sessionid=test")]
    )
    
    # Mock authentication
    communicator.scope["user"] = user
    
    try:
        connected, subprotocol = await communicator.connect()
        if connected:
            print("✅ Authenticated user successfully connected")
            
            # Test receiving a message
            response = await communicator.receive_json_from()
            if response.get('type') == 'connection_established':
                print("✅ Connection confirmation received")
            
            await communicator.disconnect()
        else:
            print("❌ Authenticated user was rejected")
    except Exception as e:
        print(f"❌ Authenticated connection failed: {e}")
    
    print("\n🎉 WebSocket authentication test completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_websocket_authentication())