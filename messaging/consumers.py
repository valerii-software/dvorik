"""WebSocket consumers for live chat updates.

The Django view that creates a Message broadcasts the rendered HTML to
the chat group; ChatConsumer is dumb — it joins/leaves the per-dialog
group and forwards whatever HTML lands on it to the client. HTMX's
WebSocket extension parses incoming HTML and applies hx-swap-oob
directives, so the new <div class="message"> appends itself to
#messages-stream automatically.
"""
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


def chat_group(dialog_id: int) -> str:
    return f'chat_{dialog_id}'


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
