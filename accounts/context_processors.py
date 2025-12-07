"""
Context processors for accounts app
"""

def user_language(request):
    """
    Add user's preferred language to all templates
    """
    if request.user.is_authenticated:
        try:
            language = request.user.preferred_language
        except:
            language = 'en'
    else:
        language = 'en'
    
    return {
        'user_language': language
    }


def unread_notifications(request):
    """
    Add unread notification count to all templates
    """
    if request.user.is_authenticated:
        try:
            unread_count = request.user.notifications.filter(is_read=False).count()
        except:
            unread_count = 0
    else:
        unread_count = 0
    
    return {
        'unread_notifications_count': unread_count
    }
