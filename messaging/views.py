from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Dialog, Message

User = get_user_model()


@login_required
def inbox(request):
    dialogs = list(Dialog.for_user(request.user))
    rows = []
    for d in dialogs:
        last = d.messages.order_by('-created_at').first()
        unread = d.messages.filter(read=False).exclude(sender=request.user).exists()
        rows.append({'dialog': d, 'other': d.other(request.user), 'last': last, 'unread': unread})
    rows.sort(key=lambda r: r['last'].created_at if r['last'] else timezone.now(), reverse=True)
    return render(request, 'messaging/inbox.html', {
        'section': 'messages',
        'rows': rows,
    })


@login_required
def open_dialog(request, user_id):
    other = get_object_or_404(User, pk=user_id)
    if other.id == request.user.id:
        return redirect('messaging:inbox')
    dialog = Dialog.get_or_create_between(request.user, other)
    dialog.messages.filter(read=False).exclude(sender=request.user).update(read=True)
    msgs = dialog.messages.select_related('sender', 'sender__profile').all()
    return render(request, 'messaging/dialog.html', {
        'section': 'messages',
        'other': other,
        'dialog': dialog,
        'messages_list': msgs,
    })


@login_required
@require_POST
def send(request, dialog_id):
    dialog = get_object_or_404(Dialog, pk=dialog_id)
    if request.user.id not in (dialog.user_a_id, dialog.user_b_id):
        return redirect('messaging:inbox')
    text = request.POST.get('text', '').strip()
    if text:
        Message.objects.create(dialog=dialog, sender=request.user, text=text)
        dialog.last_message_at = timezone.now()
        dialog.save(update_fields=['last_message_at'])
    if request.headers.get('HX-Request'):
        msgs = dialog.messages.select_related('sender', 'sender__profile').all()
        return render(request, 'messaging/_messages.html', {
            'messages_list': msgs, 'dialog': dialog, 'other': dialog.other(request.user),
        })
    return redirect('messaging:open', user_id=dialog.other(request.user).id)
