def notifications(request):
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated:
        return {}
    from django.db.models import Q
    from friends.models import Friendship
    from groups.models import GroupMember
    from messaging.models import Message
    from wall.models import WallPost

    pending = Friendship.objects.filter(
        to_user=user, status=Friendship.PENDING,
    ).count()
    unread = (
        Message.objects
        .filter(dialog__participants=user, read=False)
        .exclude(sender=user)
        .distinct()
        .count()
    )
    news_unseen = 0
    seen_at = getattr(user.profile, 'news_seen_at', None)
    if seen_at is not None:
        friend_ids = list(Friendship.friends_qs(user).values_list('id', flat=True))
        group_ids = list(
            GroupMember.objects.filter(user=user).values_list('group_id', flat=True)
        )
        news_unseen = (
            WallPost.objects
            .filter(Q(owner_id__in=friend_ids + [user.id]) | Q(group_id__in=group_ids))
            .exclude(author=user)
            .filter(created_at__gt=seen_at)
            .count()
        )
    return {
        'nav_pending_requests': pending,
        'nav_unread_messages': unread,
        'nav_news_unseen': news_unseen,
    }
