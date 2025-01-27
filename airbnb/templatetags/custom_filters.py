from django import template

register = template.Library()

@register.filter
def average_rating(review):
    return (review.cleanliness_rating + review.checkin_rating + review.value_rating) / 3

@register.filter
def to_range(value):
    """
    Returns a range object from 1 to the given value (inclusive).
    Usage in templates: {% for i in value|to_range %}
    """
    try:
        return range(1, int(value) + 1)
    except (ValueError, TypeError):
        return []