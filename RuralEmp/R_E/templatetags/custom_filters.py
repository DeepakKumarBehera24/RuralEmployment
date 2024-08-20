# myapp/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return value
