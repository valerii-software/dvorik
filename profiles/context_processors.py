from django.db.models import Q


def notifications(request):
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated:
        return {}
    from friends.models import Friendship
    from messaging.models import Dialog, Message

    pending = Friendship.objects.filter(
        to_user=user, status=Friendship.PENDING,
    ).count()
    unread = Message.objects.filter(
        Q(dialog__user_a=user) | Q(dialog__user_b=user),
        read=False,
    ).exclude(sender=user).count()
    return {
        'nav_pending_requests': pending,
        'nav_unread_messages': unread,
    }
