from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
    """Salon de discussion."""
    ROOM_TYPE_CHOICES = [
        ('admin', 'Client ↔ Admin'),
        ('support', 'Client ↔ Support'),
    ]

    room_id = models.CharField(max_length=50, unique=True, editable=False)
    participant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_rooms')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_chats'
    )
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='support')
    is_closed = models.BooleanField(default=False)
    last_message_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_rooms'
        verbose_name = 'Salon de chat'
        verbose_name_plural = 'Salons de chat'
        ordering = ['-last_message_at', '-created_at']

    def __str__(self):
        return f"Room {self.room_id} ({self.participant.username})"

    def save(self, *args, **kwargs):
        if not self.room_id:
            import uuid
            self.room_id = uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)


class Message(models.Model):
    """Message dans un salon."""
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Texte'),
        ('image', 'Image'),
        ('file', 'Fichier'),
        ('system', 'Système'),
    ]

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"