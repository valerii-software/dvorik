from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from friends.models import Friendship
from groups.models import GroupMember
from wall.models import WallPost


@login_required
def news(request):
    friend_ids = list(Friendship.friends_qs(request.user).values_list('id', flat=True))
    group_ids = list(
        GroupMember.objects.filter(user=request.user).values_list('group_id', flat=True)
    )
    posts = (
        WallPost.objects
        .filter(Q(owner_id__in=friend_ids + [request.user.id]) | Q(group_id__in=group_ids))
        .select_related('author', 'author__profile', 'owner', 'group')
        .order_by('-created_at')[:50]
    )
    return render(request, 'feed/news.html', {
        'section': 'news',
        'posts': posts,
    })
