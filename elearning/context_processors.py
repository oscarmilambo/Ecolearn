from django.utils import translation

def user_language(request):
    """
    Adds the user's preferred or active language to all templates.
    """
    lang = 'en'

    # 1️⃣ Check if user has a saved language preference
    if request.user.is_authenticated and hasattr(request.user, 'preferred_language'):
        lang = request.user.preferred_language or 'en'

    # 2️⃣ If not, use the active session language
    elif hasattr(request, 'LANGUAGE_CODE'):
        lang = request.LANGUAGE_CODE or 'en'

    # 3️⃣ Activate it for translations
    translation.activate(lang)

    return {'user_language': lang}
