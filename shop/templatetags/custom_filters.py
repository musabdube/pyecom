# shop/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiplies the value by the argument."""
    try:
        return value * arg
    except (ValueError, TypeError):
        return 0  # Return 0 if the multiplication cannot be performed
