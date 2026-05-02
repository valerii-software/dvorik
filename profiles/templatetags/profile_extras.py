from datetime import timedelta

from django import template
from django.utils import timezone

register = template.Library()

ONLINE_WINDOW = timedelta(minutes=5)


@register.filter
def is_online(profile):
    if not profile or not profile.last_seen:
        return False
    return (timezone.now() - profile.last_seen) < ONLINE_WINDOW


@register.filter
def last_seen_label(profile):
    if not profile or not profile.last_seen:
        return ''
    delta = timezone.now() - profile.last_seen
    if delta < ONLINE_WINDOW:
        return 'online'
    minutes = int(delta.total_seconds() // 60)
    if minutes < 60:
        return f'был {minutes} мин назад'
    hours = minutes // 60
    if hours < 24:
        return f'был {hours} ч назад'
    days = hours // 24
    if days < 30:
        return f'был {days} дн назад'
    return f'был {profile.last_seen:%d.%m.%Y}'
