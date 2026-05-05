"""Live wall updates: when a post lands on a user or group wall, the
open page reflects it without reload.

Wall HTML is user-specific (delete buttons depend on `request.user`),
so push_wall publishes the (kind, target_id) pair and each WallConsumer
re-renders for its own user. One render per viewer — fine for the
expected scale, and keeps templates request-aware."""
from types import SimpleNamespace

from asgiref.sync import async_to_sync

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from django.template.loader import render_to_string


def wall_group_name(kind: str, target_id: int) -> str:
    return f'wall_{kind}_{target_id}'


def push_wall(*, owner=None, group=None) -> None:
    """Tell the target's wall_*_<id> group to re-fetch and re-render."""
    layer = get_channel_layer()
    if layer is None:
        return
    if owner is not None:
        kind, target_id = 'user', owner.id
    elif group is not None:
        kind, target_id = 'group', group.id
    else:
        return
    async_to_sync(layer.group_send)(
        wall_group_name(kind, target_id),
        {'type': 'wall_update', 'kind': kind, 'target_id': target_id},
    )


class WallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        kind = self.scope['url_route']['kwargs']['kind']
        if kind not in ('user', 'group'):
            await self.close()
            return
        self.target_id = int(self.scope['url_route']['kwargs']['target_id'])
        self.user = self.scope['user']
        self.group = wall_group_name(kind, self.target_id)
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group'):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def wall_update(self, event):
        html = await self._render(event['kind'], event['target_id'])
        await self.send(text_data=html)

    @database_sync_to_async
    def _render(self, kind: str, target_id: int) -> str:
        from django.contrib.auth import get_user_model

        from groups.models import Group

        from .models import WallPost

        if kind == 'user':
            try:
                owner = get_user_model().objects.get(pk=target_id)
            except get_user_model().DoesNotExist:
                return ''
            posts = (
                WallPost.objects.filter(owner=owner)
                .select_related('author', 'author__profile')
                .prefetch_related('comments__author__profile')
            )
            ctx = {'posts': posts, 'owner': owner}
        else:
            try:
                grp = Group.objects.get(pk=target_id)
            except Group.DoesNotExist:
                return ''
            posts = (
                WallPost.objects.filter(group=grp)
                .select_related('author', 'author__profile')
                .prefetch_related('comments__author__profile')
            )
            ctx = {'posts': posts, 'group': grp}
        ctx['oob'] = True
        ctx['request'] = SimpleNamespace(user=self.user)
        return render_to_string('wall/_posts.html', ctx)
