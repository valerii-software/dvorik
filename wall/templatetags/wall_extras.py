from django import template
from django.utils.timesince import timesince

register = template.Library()


@register.filter
def vk_time(value):
    if not value:
        return ''
    delta = timesince(value).split(',')[0]
    return f'{delta} назад'
