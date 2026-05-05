from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.contrib import messages as flash
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from friends.models import Friendship
from profiles.permissions import can_view

from .consumers import chat_group, push_notif
from .models import Dialog, Message


MESSAGES_PER_PAGE = 20


def _paginate_messages(dialog, page_num):
    """Returns (messages_in_chronological_order, page_obj, page_range). Page 1 = newest."""
    qs = (
        dialog.messages
        .select_related('sender', 'sender__profile')
        .order_by('-created_at')
    )
    paginator = Paginator(qs, MESSAGES_PER_PAGE)
    page = paginator.get_page(page_num)
    page_range = list(paginator.get_elided_page_range(
        page.number, on_each_side=2, on_ends=1,
    ))
    return list(reversed(page.object_list)), page, page_range

User = get_user_model()


def _denied(request, other, message):
    return render(request, 'profiles/denied.html', {
        'pageuser': other,
        'message': message,
    }, status=403)


@login_required
def unread_count(request):
    """Cheap JSON endpoint polled by the notification JS in base.html.
    Returns new-message, pending-friend-request and unseen-news counters
    so the sidebar badges can stay in sync without a page reload."""
    from django.db.models import Q
    from friends.models import Friendship
    from groups.models import GroupMember
    from wall.models import WallPost
    n = (
        Message.objects
        .filter(dialog__participants=request.user, read=False)
        .exclude(sender=request.user)
        .distinct()
        .count()
    )
    pending = Friendship.objects.filter(
        to_user=request.user, status=Friendship.PENDING,
    ).count()
    news_unseen = 0
    seen_at = getattr(request.user.profile, 'news_seen_at', None)
    if seen_at is not None:
        friend_ids = list(Friendship.friends_qs(request.user).values_list('id', flat=True))
        group_ids = list(
            GroupMember.objects.filter(user=request.user).values_list('group_id', flat=True)
        )
        news_unseen = (
            WallPost.objects
            .filter(Q(owner_id__in=friend_ids + [request.user.id]) | Q(group_id__in=group_ids))
            .exclude(author=request.user)
            .filter(created_at__gt=seen_at)
            .count()
        )
    return JsonResponse({
        'count': n,                 # backwards-compat alias for `messages`
        'messages': n,
        'requests': pending,
        'news': news_unseen,
    })


@login_required
def inbox(request):
    chats = list(Dialog.for_user(request.user))
    rows = []
    for d in chats:
        last = d.messages.order_by('-created_at').first()
        unread = d.messages.filter(read=False).exclude(sender=request.user).exists() if not d.is_group else False
        rows.append({
            'dialog': d,
            'title': d.title_for(request.user),
            'avatar': d.avatar_for(request.user),
            'is_group': d.is_group,
            'last': last,
            'unread': unread,
        })
    rows.sort(key=lambda r: r['last'].created_at if r['last'] else timezone.now(), reverse=True)
    return render(request, 'messaging/inbox.html', {
        'section': 'messages',
        'rows': rows,
    })


@login_required
def open_dialog(request, user_id):
    """Open or create a 1-on-1 chat with the given user."""
    other = get_object_or_404(User, pk=user_id)
    if other.id == request.user.id:
        return redirect('messaging:inbox')
    dialog = Dialog.get_or_create_one_to_one(request.user, other)
    has_history = dialog.messages.exists()
    if not has_history and not can_view(request.user, other, other.profile.privacy_messages):
        return _denied(request, other, 'Этот пользователь принимает сообщения только от указанного круга людей.')
    return _render_chat(request, dialog)


@login_required
def open_chat(request, dialog_id):
    """Open any chat (1-on-1 or group) by its id."""
    dialog = get_object_or_404(Dialog, pk=dialog_id)
    if not dialog.participants.filter(pk=request.user.id).exists():
        return redirect('messaging:inbox')
    return _render_chat(request, dialog)


def _render_chat(request, dialog):
    dialog.messages.filter(read=False).exclude(sender=request.user).update(read=True)
    msgs, page, page_range = _paginate_messages(dialog, request.GET.get('page', 1))
    members = list(dialog.participants.select_related('profile').all())
    is_creator = dialog.is_group and dialog.created_by_id == request.user.id
    addable = []
    if is_creator:
        member_ids = {m.id for m in members}
        addable = [f for f in Friendship.friends_qs(request.user) if f.id not in member_ids]
    return render(request, 'messaging/dialog.html', {
        'section': 'messages',
        'dialog': dialog,
        'other': dialog.other(request.user),
        'is_group': dialog.is_group,
        'is_creator': is_creator,
        'title': dialog.title_for(request.user),
        'members': members,
        'addable_friends': addable,
        'messages_list': msgs,
        'page': page,
        'page_range': page_range,
        'ellipsis': Paginator.ELLIPSIS,
    })


@login_required
@require_POST
def send(request, dialog_id):
    dialog = get_object_or_404(Dialog, pk=dialog_id)
    if not dialog.participants.filter(pk=request.user.id).exists():
        return redirect('messaging:inbox')
    # Privacy gate only for 1-on-1, only on first message
    if not dialog.is_group:
        other = dialog.other(request.user)
        has_history = dialog.messages.exists()
        if other and not has_history and not can_view(request.user, other, other.profile.privacy_messages):
            return _denied(request, other, 'Этот пользователь принимает сообщения только от указанного круга людей.')
    text = request.POST.get('text', '').strip()
    image = request.FILES.get('image')
    if text or image:
        msg = Message.objects.create(
            dialog=dialog, sender=request.user,
            text=text, image=image,
        )
        dialog.last_message_at = timezone.now()
        dialog.save(update_fields=['last_message_at'])
        # Push the new message HTML to every WebSocket client subscribed
        # to this dialog (including the sender — keeps the bubble in
        # sync with what other clients see).
        rendered = render_to_string('messaging/_message.html', {'m': msg}, request=request)
        oob = (
            f'<div id="messages-stream" hx-swap-oob="beforeend:#messages-stream">'
            f'{rendered}</div>'
        )
        async_to_sync(get_channel_layer().group_send)(
            chat_group(dialog.id),
            {'type': 'chat_message', 'html': oob},
        )
        # Update inbox/sidebar counters for everyone except the sender.
        for participant_id in dialog.participants.exclude(id=request.user.id).values_list('id', flat=True):
            push_notif(participant_id)
    if request.headers.get('HX-Request'):
        return HttpResponse(status=204)
    return redirect('messaging:open_chat', dialog_id=dialog.id)


@login_required
def create_group(request):
    """Create a new group chat with selected friends."""
    friends = list(Friendship.friends_qs(request.user))
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        member_ids = [int(i) for i in request.POST.getlist('members') if i.isdigit()]
        if not name:
            flash.error(request, 'Укажите название чата.')
        elif not member_ids:
            flash.error(request, 'Выберите хотя бы одного участника.')
        else:
            friend_ids = {f.id for f in friends}
            valid_ids = [i for i in member_ids if i in friend_ids]
            dialog = Dialog.objects.create(
                name=name[:120],
                created_by=request.user,
            )
            dialog.participants.add(request.user, *valid_ids)
            return redirect('messaging:open_chat', dialog_id=dialog.id)
    return render(request, 'messaging/create_group.html', {
        'section': 'messages',
        'friends': friends,
    })


@login_required
@require_POST
def leave_chat(request, dialog_id):
    dialog = get_object_or_404(Dialog, pk=dialog_id)
    if not dialog.is_group:
        return redirect('messaging:inbox')
    if dialog.participants.filter(pk=request.user.id).exists():
        dialog.participants.remove(request.user)
        flash.info(request, f'Вы покинули чат «{dialog.name}».')
    return redirect('messaging:inbox')


@login_required
@require_POST
def add_members(request, dialog_id):
    dialog = get_object_or_404(Dialog, pk=dialog_id)
    if not dialog.is_group or dialog.created_by_id != request.user.id:
        return redirect('messaging:open_chat', dialog_id=dialog.id)
    member_ids = [int(i) for i in request.POST.getlist('members') if i.isdigit()]
    friend_ids = {f.id for f in Friendship.friends_qs(request.user)}
    valid = [i for i in member_ids if i in friend_ids]
    if valid:
        dialog.participants.add(*valid)
        flash.success(request, f'Добавлено: {len(valid)}.')
    return redirect('messaging:open_chat', dialog_id=dialog.id)


@login_required
@require_POST
def remove_member(request, dialog_id, user_id):
    dialog = get_object_or_404(Dialog, pk=dialog_id)
    if not dialog.is_group or dialog.created_by_id != request.user.id:
        return redirect('messaging:open_chat', dialog_id=dialog.id)
    if user_id == request.user.id:
        return redirect('messaging:open_chat', dialog_id=dialog.id)
    dialog.participants.remove(user_id)
    return redirect('messaging:open_chat', dialog_id=dialog.id)
