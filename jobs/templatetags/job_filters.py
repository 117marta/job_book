from django import template
from django.core.paginator import Paginator

register = template.Library()


@register.filter
def km(value):
    """
    Returns a `+` as a seperator.
    """
    return str(value).replace(".", "+")


@register.simple_tag
def get_elided_page_range(paginator, number, on_each_side=2, on_ends=1):
    """
    Returns a 1-based list of page numbers.
    """
    paginator = Paginator(paginator.object_list, paginator.per_page)
    return paginator.get_elided_page_range(
        number=number, on_each_side=on_each_side, on_ends=on_ends
    )
