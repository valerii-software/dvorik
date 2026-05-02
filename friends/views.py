from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
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
    results = User.objects.none()
    if q or city:
        qs = User.objects.exclude(id=request.user.id).select_related('profile')
        if q:
            for token in q.split():
                qs = qs.filter(Q(first_name__icontains=token) | Q(last_name__icontains=token))
        if city:
            qs = qs.filter(profile__home_city__icontains=city)
        results = qs[:50]
    return render(request, 'friends/search.html', {
        'section': 'search',
        'q': q,
        'city': city,
        'results': results,
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
    else:
        Friendship.objects.create(from_user=request.user, to_user=other)
        messages.success(request, f'Заявка отправлена пользователю {other.first_name}.')
    return redirect('profiles:view', user_id=user_id)


@login_required
@require_POST
def cancel(request, user_id):
    Friendship.objects.filter(
        from_user=request.user, to_user_id=user_id, status=Friendship.PENDING
    ).delete()
    return redirect('profiles:view', user_id=user_id)


@login_required
@require_POST
def accept(request, user_id):
    f = get_object_or_404(Friendship, from_user_id=user_id, to_user=request.user, status=Friendship.PENDING)
    f.status = Friendship.ACCEPTED
    f.accepted_at = timezone.now()
    f.save()
    messages.success(request, 'Заявка принята.')
    return redirect('friends:requests')


@login_required
@require_POST
def reject(request, user_id):
    Friendship.objects.filter(
        from_user_id=user_id, to_user=request.user, status=Friendship.PENDING
    ).delete()
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
