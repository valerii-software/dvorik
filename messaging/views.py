from django.contrib import messages as flash
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from friends.models import Friendship
from profiles.permissions import can_view

from .models import Dialog, Message

User = get_user_model()


def _denied(request, other, message):
    return render(request, 'profiles/denied.html', {
        'pageuser': other,
        'message': message,
    }, status=403)


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
    msgs = dialog.messages.select_related('sender', 'sender__profile').all()
    members = list(dialog.participants.select_related('profile').all())
    return render(request, 'messaging/dialog.html', {
        'section': 'messages',
        'dialog': dialog,
        'other': dialog.other(request.user),
        'is_group': dialog.is_group,
        'title': dialog.title_for(request.user),
        'members': members,
        'messages_list': msgs,
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
        Message.objects.create(
            dialog=dialog, sender=request.user,
            text=text, image=image,
        )
        dialog.last_message_at = timezone.now()
        dialog.save(update_fields=['last_message_at'])
    if request.headers.get('HX-Request'):
        msgs = dialog.messages.select_related('sender', 'sender__profile').all()
        return render(request, 'messaging/_messages.html', {
            'messages_list': msgs, 'dialog': dialog,
        })
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
