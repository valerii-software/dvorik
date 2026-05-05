"""WebSocket consumers for live updates.

ChatConsumer (per-dialog) — appends new messages to the open chat.
NotificationConsumer (per-user) — pushes counter snapshots so the
sidebar badges and notification sound react in real time instead
of polling /messages/unread-count/ every 10s.
"""
from asgiref.sync import async_to_sync

from channels.db import database_sync_to_async
from channels.generic.websocket import (
    AsyncJsonWebsocketConsumer,
    AsyncWebsocketConsumer,
)
from channels.layers import get_channel_layer


def chat_group(dialog_id: int) -> str:
    return f'chat_{dialog_id}'


def notif_group(user_id: int) -> str:
    return f'notif_{user_id}'


def get_notif_snapshot(user) -> dict:
    """Re-query all per-user counters. Cheap (3 indexed counts)."""
    from django.db.models import Q

    from friends.models import Friendship
    from groups.models import GroupMember
    from messaging.models import Message
    from wall.models import WallPost

    n_msg = (
        Message.objects
        .filter(dialog__participants=user, read=False)
        .exclude(sender=user)
        .distinct()
        .count()
    )
    n_req = Friendship.objects.filter(
        to_user=user, status=Friendship.PENDING,
    ).count()
    seen_at = getattr(user.profile, 'news_seen_at', None)
    if seen_at is None:
        n_news = 0
    else:
        friend_ids = list(Friendship.friends_qs(user).values_list('id', flat=True))
        group_ids = list(
            GroupMember.objects.filter(user=user).values_list('group_id', flat=True)
        )
        n_news = (
            WallPost.objects
            .filter(Q(owner_id__in=friend_ids + [user.id]) | Q(group_id__in=group_ids))
            .exclude(author=user)
            .filter(created_at__gt=seen_at)
            .count()
        )
    return {'messages': n_msg, 'requests': n_req, 'news': n_news}


def push_notif(user_id: int) -> None:
    """Re-query the user's snapshot and broadcast to their notif group.
    Called from inside synchronous Django views — wraps async_to_sync."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.select_related('profile').get(pk=user_id)
    except User.DoesNotExist:
        return
    layer = get_channel_layer()
    if layer is None:
        return
    async_to_sync(layer.group_send)(
        notif_group(user_id),
        {'type': 'notif_update', 'data': get_notif_snapshot(user)},
    )


def push_notif_for_wall_post(wp) -> None:
    """Notify everyone whose news feed contains this fresh wall post."""
    from friends.models import Friendship
    from groups.models import GroupMember

    if wp.owner_id:
        friend_ids = list(
            Friendship.friends_qs(wp.owner).values_list('id', flat=True)
        )
        recipients = set(friend_ids) | {wp.owner_id}
    elif wp.group_id:
        recipients = set(
            GroupMember.objects.filter(group_id=wp.group_id).values_list('user_id', flat=True)
        )
    else:
        return
    recipients.discard(wp.author_id)
    for uid in recipients:
        push_notif(uid)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.dialog_id = int(self.scope['url_route']['kwargs']['dialog_id'])
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return
        if not await self._is_participant(user.id, self.dialog_id):
            await self.close()
            return
        self.group = chat_group(self.dialog_id)
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group'):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def chat_message(self, event):
        # `event['html']` is a fully-rendered fragment with hx-swap-oob.
        await self.send(text_data=event['html'])

    @staticmethod
    @database_sync_to_async
    def _is_participant(user_id: int, dialog_id: int) -> bool:
        from .models import Dialog
        return Dialog.objects.filter(pk=dialog_id, participants__id=user_id).exists()


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return
        self.group = notif_group(user.id)
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        # Initial snapshot so the client renders the right badges
        # without waiting for the first event.
        snapshot = await database_sync_to_async(self._snapshot)(user)
        await self.send_json(snapshot)

    async def disconnect(self, close_code):
        if hasattr(self, 'group'):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def notif_update(self, event):
        await self.send_json(event['data'])

    @staticmethod
    def _snapshot(user):
        return get_notif_snapshot(user)
