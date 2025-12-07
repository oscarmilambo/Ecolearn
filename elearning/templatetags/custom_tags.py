from django import template

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