from django import template
from datetime import timedelta, datetime

# Register the template library only once
register = template.Library()

# Custom filter to get an item from a dictionary using its key
@register.filter
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary using its key.
    Usage: {{ my_dict|get_item:key }}
    """
    return dictionary.get(key)

# Custom filter to add days to a given date
@register.filter
def add_days(value, days):
    """Adds a specified number of days to a given date."""
    if isinstance(value, (str, int, float)):
        value = datetime.strptime(value, "%Y-%m-%d").date()
    return value + timedelta(days=days)
