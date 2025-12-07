# elearning/middleware.py
from django.utils import translation

class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # SAFE: request.user exists now
        lang_code = 'en'

        if hasattr(request, 'user') and request.user.is_authenticated:
            lang_code = getattr(request.user, 'preferred_language', 'en') or 'en'

        # Fallback: session (from language switcher)
        elif request.session.get('ecolearn_language'):
            lang_code = request.session['ecolearn_language']

        # Validate
        if lang_code not in {'en', 'bem', 'ny'}:
            lang_code = 'en'

        # ACTIVATE
        translation.activate(lang_code)
        request.LANGUAGE_CODE = lang_code

        response = self.get_response(request)
        response['Content-Language'] = lang_code
        return response