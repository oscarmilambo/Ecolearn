# accounts/middleware.py
"""
Custom middleware to activate user's preferred language
"""

from django.utils import translation
from django.conf import settings


class UserLanguageMiddleware:
    """
    Middleware to activate the user's preferred language from their profile.
    This runs after Django's LocaleMiddleware.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user is authenticated and has a preferred language
        if request.user.is_authenticated and hasattr(request.user, 'preferred_language'):
            user_language = request.user.preferred_language
            
            # Validate it's a supported language
            valid_languages = [lang[0] for lang in settings.LANGUAGES]
            
            if user_language and user_language in valid_languages:
                # Activate the user's preferred language
                translation.activate(user_language)
                request.LANGUAGE_CODE = user_language
        
        response = self.get_response(request)
        return response
