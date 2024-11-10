from django import template

register = template.Library()

@register.filter
def get_json_value(value, arg):
    return value.get(arg)