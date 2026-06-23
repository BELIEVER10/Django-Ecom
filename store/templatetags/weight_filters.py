from django import template

register = template.Library()

@register.filter
def kg_to_g(value):
    """Convert kilograms to grams."""
    if value is None:
        return ''
    try:
        grams = float(value) * 1000
        return f"{grams:.0f}"  # no decimal, whole grams
    except (ValueError, TypeError):
        return value