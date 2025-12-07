"""
WebSocket Consumers for real-time features
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            # Create a unique group name for this user
            self.group_name = f"notifications_{self.user.id}"
            
            # Join the user's notification group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if self.user.is_authenticated:
            # Leave the notification group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'ping')
            
            if message_type == 'ping':
                # Respond to ping with pong
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
        except json.JSONDecodeError:
            pass
    
    async def notification_message(self, event):
        """Handle notification messages from the group"""
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))


class DashboardConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for dashboard real-time updates"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            self.group_name = f"dashboard_{self.user.id}"
            
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'ping')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
        except json.JSONDecodeError:
            pass
    
    async def dashboard_update(self, event):
        """Handle dashboard update messages"""
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': event['data']
        }))


class AdminDashboardConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for admin dashboard real-time updates"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        if self.user.is_authenticated and self.user.is_staff:
            self.group_name = "admin_dashboard"
            
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'ping')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
        except json.JSONDecodeError:
            pass
    
    async def admin_update(self, event):
        """Handle admin dashboard update messages"""
        await self.send(text_data=json.dumps({
            'type': 'admin_update',
            'data': event['data']
        }))


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for chat functionality"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"
        
        if self.user.is_authenticated:
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Send join notification
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': f'{self.user.username} joined the chat',
                    'username': 'System',
                    'user_id': None
                }
            )
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if self.user.is_authenticated:
            # Send leave notification
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': f'{self.user.username} left the chat',
                    'username': 'System',
                    'user_id': None
                }
            )
            
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message = data.get('message', '')
            
            if message:
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'username': self.user.username,
                        'user_id': self.user.id
                    }
                )
        except json.JSONDecodeError:
            pass
    
    async def chat_message(self, event):
        """Handle chat messages from the group"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'user_id': event.get('user_id')
        }))