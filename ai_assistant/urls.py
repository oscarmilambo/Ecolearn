from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.chat_interface, name='chat'),
    path('send/', views.send_message, name='send_message'),
    path('sessions/', views.get_chat_sessions, name='get_sessions'),
    path('session/<int:session_id>/', views.get_session_messages, name='get_session'),
    path('session/new/', views.new_session, name='new_session'),
    path('session/<int:session_id>/delete/', views.delete_session, name='delete_session'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
]
