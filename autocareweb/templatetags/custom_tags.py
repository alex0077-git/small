from django import template
from ..models import Vehicle

register = template.Library()

@register.filter
def get_selected_vehicle(vehicles, selected_vehicle_id):
    try:
        return Vehicle.objects.get(id=selected_vehicle_id)
    except Vehicle.DoesNotExist:
        return None
    

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Filter to get an item from a dictionary using its key
    Usage: {{ my_dict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(str(key) if isinstance(key, int) else key)