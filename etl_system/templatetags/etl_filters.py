# etl_system/templatetags/etl_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def mul(value, arg):
    """Multiply the value by the arg"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def make_range(value):
    """Create a range from 1 to value"""
    try:
        return range(1, int(value) + 1)
    except (ValueError, TypeError):
        return range(0)

@register.filter
def unique_values(queryset, field_name):
    """Get unique values for a specific field from a queryset"""
    try:
        unique_vals = set()
        for item in queryset:
            value = getattr(item, field_name, None)
            if value:
                unique_vals.add(value)
        return len(unique_vals)
    except:
        return 0

@register.filter
def count_unique_databases(tables):
    """Count unique target databases"""
    try:
        databases = set()
        for table in tables:
            if hasattr(table, 'TGT_DATABASE') and table.TGT_DATABASE:
                databases.add(table.TGT_DATABASE)
        return len(databases)
    except:
        return 0

@register.filter
def count_unique_schemas(tables):
    """Count unique target schemas"""
    try:
        schemas = set()
        for table in tables:
            if hasattr(table, 'TGT_SCHEMA') and table.TGT_SCHEMA:
                schemas.add(table.TGT_SCHEMA)
        return len(schemas)
    except:
        return 0