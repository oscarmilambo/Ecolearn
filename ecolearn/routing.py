"""
WebSocket URL routing for Django Channels
"""
from django.urls import path
from channels.routing import URLRouter
from . import consumers

websocket_urlpatterns = [
    # Notifications WebSocket
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
    
    # Dashboard updates WebSocket
    path('ws/dashboard/', consumers.DashboardConsumer.as_asgi()),
    
    # Admin dashboard WebSocket
    path('ws/admin-dashboard/', consumers.AdminDashboardConsumer.as_asgi()),
    
    # Chat WebSocket (for future chat features)
    path('ws/chat/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
]
