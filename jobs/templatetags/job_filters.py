from django import template

register = template.Library()


@register.filter
def km(value):
    return str(value).replace(".", "+")
