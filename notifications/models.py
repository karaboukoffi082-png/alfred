from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Notification utilisateur."""
    TYPE_CHOICES = [
        ('order', 'Commande'),
        ('pressing', 'Pressing'),
        ('fai', 'Internet'),
        ('chat', 'Message'),
        ('payment', 'Paiement'),
        ('system', 'Système'),
        ('promo', 'Promotion'),
    ]
    CHANNEL_CHOICES = [
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('sms', 'SMS'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type_notif = models.CharField(max_length=15, choices=TYPE_CHOICES, default='system')
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='in_app')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=300, blank=True, help_text="URL de redirection")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.title} → {self.user.username}"