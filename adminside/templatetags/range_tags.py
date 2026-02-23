from django import template

register = template.Library()


@register.simple_tag
def range_list(count):
    return range(int(count))
