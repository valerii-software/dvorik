from datetime import timedelta

from django.utils import timezone


THROTTLE = timedelta(seconds=60)


class LastSeenMiddleware:
    """Updates Profile.last_seen on each request, no more than once per minute."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            try:
                profile = user.profile
            except Exception:
                return response
            now = timezone.now()
            if not profile.last_seen or (now - profile.last_seen) > THROTTLE:
                profile.last_seen = now
                profile.save(update_fields=['last_seen'])
        return response
