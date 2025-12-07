from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Template filter to get dictionary value by key.
    Usage: {{ progress_map|get_item:lesson.id }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter(name='percentage')
def percentage(value, total):
    """
    Calculate percentage.
    Usage: {{ completed|percentage:total }}
    """
    try:
        if not total or total == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0


@register.filter(name='duration_format')
def duration_format(minutes):
    """
    Format duration in minutes to human-readable format.
    Usage: {{ duration_minutes|duration_format }}
    """
    try:
        minutes = int(minutes)
        if minutes < 0:
            return "0 min"
        if minutes < 60:
            return f"{minutes} min"
        hours = minutes // 60
        mins = minutes % 60
        if mins == 0:
            return f"{hours} hr"
        return f"{hours} hr {mins} min"
    except (ValueError, TypeError):
        return "0 min"


@register.filter(name='content_type_icon')
def content_type_icon(content_type):
    """
    Return FontAwesome icon class for content type.
    """
    icons = {
        'video': 'fa-video',
        'audio': 'fa-headphones',
        'text': 'fa-file-alt',
        'quiz': 'fa-question-circle',
        'interactive': 'fa-laptop-code',
    }
    return icons.get(content_type.lower(), 'fa-file')


@register.filter(name='difficulty_icon')
def difficulty_icon(difficulty):
    """
    Return FontAwesome icon class for difficulty level.
    """
    icons = {
        'beginner': 'fa-seedling',
        'intermediate': 'fa-chart-line',
        'advanced': 'fa-trophy',
        'expert': 'fa-crown',
    }
    return icons.get(difficulty.lower(), 'fa-circle')


@register.filter(name='difficulty_color')
def difficulty_color(difficulty):
    """
    Return color class for difficulty level.
    """
    colors = {
        'beginner': 'green',
        'intermediate': 'yellow',
        'advanced': 'red',
        'expert': 'purple',
    }
    return colors.get(difficulty.lower(), 'gray')


@register.filter(name='time_ago')
def time_ago(date):
    """
    Convert date to 'time ago' format.
    """
    if not date:
        return ''
    
    now = timezone.now()
    diff = now - date
    
    if diff < timedelta(minutes=1):
        return 'just now'
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f'{minutes} min{"s" if minutes > 1 else ""} ago'
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f'{hours} hr{"s" if hours > 1 else ""} ago'
    elif diff < timedelta(days=30):
        days = diff.days
        return f'{days} day{"s" if days > 1 else ""} ago'
    elif diff < timedelta(days=365):
        months = int(diff.days / 30)
        return f'{months} month{"s" if months > 1 else ""} ago'
    else:
        years = int(diff.days / 365)
        return f'{years} year{"s" if years > 1 else ""} ago'


@register.filter(name='completion_badge')
def completion_badge(is_completed, percentage=None):
    """
    Return completion badge HTML.
    Usage: {{ lesson_progress.is_completed|completion_badge }}
    """
    if is_completed or (percentage and percentage >= 100):
        return mark_safe('<span class="badge badge-success"><i class="fas fa-check-circle"></i> Completed</span>')
    elif percentage and percentage > 0:
        return mark_safe(f'<span class="badge badge-warning"><i class="fas fa-clock"></i> {percentage}% In Progress</span>')
    else:
        return mark_safe('<span class="badge badge-secondary"><i class="fas fa-circle"></i> Not Started</span>')


@register.filter(name='truncate_words')
def truncate_words(text, num_words):
    """
    Truncate text to specified number of words.
    """
    try:
        num_words = int(num_words)
        if num_words <= 0:
            return ''
        words = str(text).split()
        if len(words) <= num_words:
            return text
        return ' '.join(words[:num_words]) + '...'
    except (ValueError, TypeError):
        return text


@register.simple_tag
def progress_percentage(enrollment):
    """
    Calculate progress percentage for an enrollment.
    Usage: {% progress_percentage enrollment %}
    """
    if not enrollment:
        return 0
    return round(enrollment.progress_percentage, 1)


@register.filter
def star_rating(rating):
    """
    Convert rating to star display.
    Usage: {{ course.rating|star_rating }}
    """
    try:
        rating = float(rating)
        if rating < 0 or rating > 5:
            return '☆☆☆☆☆'
        full_stars = int(rating)
        half_star = 1 if rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        stars = '★' * full_stars
        if half_star:
            stars += '½'
        stars += '☆' * empty_stars
        
        return stars
    except (ValueError, TypeError):
        return '☆☆☆☆☆'


@register.simple_tag(takes_context=True)
def get_translated_media(context, lesson, media_type):
    """
    Return correct media file for selected language.
    """
    request = context.get('request')
    user_language = (
        getattr(request.user, 'preferred_language', None)
        or request.session.get('django_language')
        or context.get('user_language', 'en')
    )
    
    if media_type == 'video':
        lang_file = getattr(lesson, f"video_file_{user_language}", None)
        return lang_file or lesson.video_file

    elif media_type == 'audio':
        lang_file = getattr(lesson, f"audio_file_{user_language}", None)
        return lang_file or lesson.audio_file

    return None

@register.filter(name='make_list')
def make_list(value):
    """Convert string to list of characters"""
    return list(str(value))

@register.simple_tag(takes_context=True)
def get_translated_field(context, obj, field_name):
    """
    Get translated field value (English, Bemba, or Nyanja)
    """
    request = context.get('request')
    user_language = (
        getattr(request.user, 'preferred_language', None)
        or request.session.get('django_language')
        or context.get('user_language', 'en')
    )

    lang_field = f"{field_name}_{user_language}"
    translated_value = getattr(obj, lang_field, None)
    if translated_value:
        return translated_value

    return getattr(obj, field_name, '')