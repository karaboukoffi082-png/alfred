import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope["user"]

        # ❌ Refuser si non connecté
        if not self.user.is_authenticated:
            await self.close()
            return

        # ✅ Vérifier accès au salon
        has_access = await self.check_room_access()
        if not has_access:
            await self.close()
            return

        # ✅ Rejoindre groupe
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        message_type = data.get('type', 'text')
        content = data.get('content', '').strip()
        file_url = data.get('file_url', '')

        if message_type == 'text' and not content:
            return

        # ✅ Sauvegarde message
        message = await self.save_message(message_type, content, file_url)

        # ✅ Envoi au groupe
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': message.id,
                'sender_id': self.user.id,
                'sender_name': self.user.get_full_name() or self.user.username,
                'sender_avatar': self.user.avatar.url if getattr(self.user, 'avatar', None) else '',
                'message_type': message_type,
                'content': content,
                'file_url': file_url,
                'created_at': message.created_at.isoformat(),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def check_room_access(self):
        from chat.models import ChatRoom

        try:
            room = ChatRoom.objects.get(room_id=self.room_id)
            user = self.user

            return (
                room.participant == user
                or room.assigned_to == user
                or getattr(user, "is_admin_user", False)
            )

        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, message_type, content, file_url):
        from chat.models import ChatRoom, Message

        room = ChatRoom.objects.get(room_id=self.room_id)

        msg = Message.objects.create(
            room=room,
            sender=self.user,
            message_type=message_type,
            content=content if message_type == 'text' else '',
            file=file_url if message_type in ('image', 'file') else None,
        )

        room.last_message_at = msg.created_at
        room.save(update_fields=['last_message_at'])

        return msg