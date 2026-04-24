from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .models import Notification


class NotificationService:
    """Service centralisé d'envoi de notifications."""

    @staticmethod
    def send(user, type_notif, title, message, link='', channel='in_app'):
        """Envoyer une notification."""
        # Toujours en in-app
        Notification.objects.create(
            user=user,
            type_notif=type_notif,
            channel=channel,
            title=title,
            message=message,
            link=link,
        )

        # Email si configuré
        if channel in ('email', 'in_app') and user.email:
            NotificationService._send_email(user, title, message)

        # SMS si configuré
        if channel in ('sms', 'in_app') and user.phone:
            NotificationService._send_sms(user.phone, message)

    @staticmethod
    def _send_email(user, subject, message):
        try:
            html_message = render_to_string('notifications/email_template.html', {
                'user': user,
                'subject': subject,
                'message': message,
            })
            send_mail(
                subject=f'[DK-PRESS] {subject}',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception:
            pass

    @staticmethod
    def _send_sms(phone, message):
        """Intégration SMS (à implémenter selon le fournisseur)."""
        try:
            # Exemple avec une API SMS
            import requests
            response = requests.post(
                settings.SMS_API_URL,
                json={'to': phone, 'message': message},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False