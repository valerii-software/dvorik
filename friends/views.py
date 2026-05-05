from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Value
from django.db.models.functions import Concat, Lower
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Friendship

User = get_user_model()


@login_required
def my_friends(request):
    friends = Friendship.friends_qs(request.user)
    return render(request, 'friends/list.html', {
        'section': 'friends',
        'pageuser': request.user,
        'friends': friends,
        'is_me': True,
    })


@login_required
def user_friends(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    friends = Friendship.friends_qs(user)
    return render(request, 'friends/list.html', {
        'pageuser': user,
        'friends': friends,
        'is_me': user.id == request.user.id,
    })


@login_required
def requests_view(request):
    incoming = Friendship.incoming_requests(request.user)
    outgoing = Friendship.outgoing_requests(request.user)
    return render(request, 'friends/requests.html', {
        'section': 'requests',
        'incoming': incoming,
        'outgoing': outgoing,
    })


@login_required
def search(request):
    q = request.GET.get('q', '').strip()
    city = request.GET.get('city', '').strip()
    qs = (
        User.objects
        .exclude(id=request.user.id)
        .select_related('profile')
        .annotate(name_lower=Lower(Concat('first_name', Value(' '), 'last_name')))
        .order_by('first_name', 'last_name', 'id')
    )
    if q:
        for token in q.split():
            qs = qs.filter(name_lower__contains=token.lower())
    if city:
        qs = qs.annotate(city_lower=Lower('profile__home_city')).filter(city_lower__contains=city.lower())

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'friends/search.html', {
        'section': 'search',
        'q': q,
        'city': city,
        'page': page,
        'total': paginator.count,
        'has_query': bool(q or city),
    })


@login_required
@require_POST
def add(request, user_id):
    if user_id == request.user.id:
        return redirect('profiles:my_page')
    other = get_object_or_404(User, pk=user_id)
    existing = Friendship.objects.filter(
        Q(from_user=request.user, to_user=other) | Q(from_user=other, to_user=request.user)
    ).first()
    if existing:
        if existing.status == Friendship.PENDING and existing.to_user_id == request.user.id:
            existing.status = Friendship.ACCEPTED
            existing.accepted_at = timezone.now()
            existing.save()
            messages.success(request, f'Вы стали друзьями с {other.first_name}.')
            from messaging.consumers import push_notif
            push_notif(request.user.id)
            push_notif(other.id)
    else:
        Friendship.objects.create(from_user=request.user, to_user=other)
        messages.success(request, f'Заявка отправлена пользователю {other.first_name}.')
        from messaging.consumers import push_notif
        push_notif(other.id)
    return redirect('profiles:view', user_id=user_id)


@login_required
@require_POST
def cancel(request, user_id):
    Friendship.objects.filter(
        from_user=request.user, to_user_id=user_id, status=Friendship.PENDING
    ).delete()
    from messaging.consumers import push_notif
    push_notif(user_id)  # the recipient's pending counter just dropped
    return redirect('profiles:view', user_id=user_id)


@login_required
@require_POST
def accept(request, user_id):
    f = get_object_or_404(Friendship, from_user_id=user_id, to_user=request.user, status=Friendship.PENDING)
    f.status = Friendship.ACCEPTED
    f.accepted_at = timezone.now()
    f.save()
    messages.success(request, 'Заявка принята.')
    from messaging.consumers import push_notif
    push_notif(request.user.id)
    return redirect('friends:requests')


@login_required
@require_POST
def reject(request, user_id):
    Friendship.objects.filter(
        from_user_id=user_id, to_user=request.user, status=Friendship.PENDING
    ).delete()
    from messaging.consumers import push_notif
    push_notif(request.user.id)
    return redirect('friends:requests')


@login_required
@require_POST
def remove(request, user_id):
    Friendship.objects.filter(
        Q(from_user=request.user, to_user_id=user_id) |
        Q(from_user_id=user_id, to_user=request.user),
        status=Friendship.ACCEPTED,
    ).delete()
    messages.info(request, 'Удалено из друзей.')
    return redirect('profiles:view', user_id=user_id)
