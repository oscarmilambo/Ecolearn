from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import google.generativeai as genai
import json
from .models import ChatSession, ChatMessage, AssistantFeedback


# Configure Gemini AI
genai.configure(api_key=settings.GEMINI_API_KEY)


def get_system_context():
    """Provide context about the EcoLearn system to the AI"""
    return """You are EcoLearn AI Assistant, a helpful guide for the EcoLearn Zambia environmental education platform.

SYSTEM OVERVIEW:
- EcoLearn is an environmental education platform for Zambia
- Focuses on waste management, recycling, and sustainable practices
- Supports English, Bemba, and Nyanja languages
- Serves communities across Zambia

KEY FEATURES YOU CAN HELP WITH:
1. Learning Modules - Interactive courses on waste management
2. Community Forum - Discussion boards for sharing best practices
3. Events - Community cleanup events and workshops
4. Reporting - Report illegal dumping sites
5. Success Stories - Share environmental achievements
6. Challenges - Join community cleanup challenges
7. Health Alerts - Emergency environmental health notifications
8. Points & Rewards - Earn points for activities, redeem for rewards
9. Groups - Form cleanup groups with other users
10. Certificates - Earn certificates for completing modules

NAVIGATION HELP:
- Dashboard: /accounts/dashboard/
- Learning Modules: /elearning/modules/
- Forum: /community/forum/
- Events: /community/events/
- Report Dumping: /reporting/report/
- My Progress: /elearning/app/dashboard/
- My Impact: /community/my-impact/
- Health Alerts: /community/health-alerts/

YOUR ROLE:
- Help users navigate the platform
- Answer questions about features
- Provide guidance on waste management
- Explain how to use different features
- Be friendly, helpful, and encouraging
- Respond in the user's preferred language if they specify
- Keep responses concise and actionable

IMPORTANT:
- Always be positive and encouraging about environmental action
- Provide specific navigation instructions when asked
- If you don't know something, admit it and suggest contacting support
- Promote community engagement and environmental awareness
"""


@login_required
def chat_interface(request):
    """Main chat interface"""
    # Get or create active session
    session = ChatSession.objects.filter(
        user=request.user,
        is_active=True
    ).first()
    
    if not session:
        session = ChatSession.objects.create(
            user=request.user,
            title='New Chat'
        )
    
    # Get recent sessions
    recent_sessions = ChatSession.objects.filter(
        user=request.user
    )[:10]
    
    context = {
        'session': session,
        'recent_sessions': recent_sessions,
    }
    return render(request, 'ai_assistant/chat.html', context)


@login_required
@require_http_methods(["POST"])
def send_message(request):
    """Handle sending messages to AI"""
    try:
        data = json.loads(request.body)
        message_content = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message_content:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Get or create session
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(
                user=request.user,
                title=message_content[:50]
            )
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            role='user',
            content=message_content
        )
        
        # Get conversation history
        history = []
        previous_messages = ChatMessage.objects.filter(
            session=session
        ).order_by('created_at')[:20]  # Last 20 messages for context
        
        for msg in previous_messages:
            if msg.role != 'system':
                history.append({
                    'role': 'user' if msg.role == 'user' else 'model',
                    'parts': [msg.content]
                })
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-pro')
        
        # Start chat with history
        chat = model.start_chat(history=history[:-1])  # Exclude the current message
        
        # Add system context
        full_prompt = f"{get_system_context()}\n\nUser Question: {message_content}"
        
        # Get AI response
        response = chat.send_message(full_prompt)
        ai_response = response.text
        
        # Save AI response
        assistant_message = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=ai_response
        )
        
        return JsonResponse({
            'success': True,
            'session_id': session.id,
            'user_message': {
                'id': user_message.id,
                'content': user_message.content,
                'created_at': user_message.created_at.isoformat()
            },
            'assistant_message': {
                'id': assistant_message.id,
                'content': assistant_message.content,
                'created_at': assistant_message.created_at.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
def get_session_messages(request, session_id):
    """Get all messages for a session"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    messages = ChatMessage.objects.filter(session=session).order_by('created_at')
    
    messages_data = [{
        'id': msg.id,
        'role': msg.role,
        'content': msg.content,
        'created_at': msg.created_at.isoformat()
    } for msg in messages]
    
    return JsonResponse({
        'session_id': session.id,
        'title': session.title,
        'messages': messages_data
    })


@login_required
@require_http_methods(["POST"])
def new_session(request):
    """Create a new chat session"""
    # Mark current session as inactive
    ChatSession.objects.filter(
        user=request.user,
        is_active=True
    ).update(is_active=False)
    
    # Create new session
    session = ChatSession.objects.create(
        user=request.user,
        title='New Chat'
    )
    
    return JsonResponse({
        'success': True,
        'session_id': session.id
    })


@login_required
@require_http_methods(["POST"])
def delete_session(request, session_id):
    """Delete a chat session"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    session.delete()
    
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def submit_feedback(request):
    """Submit feedback on AI response"""
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        message = get_object_or_404(ChatMessage, id=message_id)
        
        feedback = AssistantFeedback.objects.create(
            message=message,
            user=request.user,
            rating=rating,
            comment=comment
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
