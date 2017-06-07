from django import template

register = template.Library()

@register.filter
def classname(obj):
    return obj.__class__.__name__

@register.filter
def fieldtype(field):
    return field.field.widget.__class__.__name__
