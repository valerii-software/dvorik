"""Live wall updates: when a post lands on a user or group wall, the
open page reflects it without reload."""
from asgiref.sync import async_to_sync

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from django.template.loader import render_to_string


def wall_group_name(kind: str, target_id: int) -> str:
    return f'wall_{kind}_{target_id}'


def push_wall(*, owner=None, group=None) -> None:
    """Re-render the target's #wall-posts and broadcast to subscribers.
    Pass exactly one of (owner, group)."""
    from .models import WallPost

    layer = get_channel_layer()
    if layer is None:
        return
    if owner is not None:
        kind = 'user'
        target_id = owner.id
        posts = (
            WallPost.objects.filter(owner=owner)
            .select_related('author', 'author__profile')
        )
        ctx = {'posts': posts, 'owner': owner, 'oob': True}
    elif group is not None:
        kind = 'group'
        target_id = group.id
        posts = (
            WallPost.objects.filter(group=group)
            .select_related('author', 'author__profile')
        )
        ctx = {'posts': posts, 'group': group, 'oob': True}
    else:
        return
    html = render_to_string('wall/_posts.html', ctx)
    async_to_sync(layer.group_send)(
        wall_group_name(kind, target_id),
        {'type': 'wall_update', 'html': html},
    )


class WallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        kind = self.scope['url_route']['kwargs']['kind']
        if kind not in ('user', 'group'):
            await self.close()
            return
        target_id = int(self.scope['url_route']['kwargs']['target_id'])
        self.group = wall_group_name(kind, target_id)
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group'):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def wall_update(self, event):
        await self.send(text_data=event['html'])
