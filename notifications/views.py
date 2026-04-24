from django.shortcuts import render
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """Liste des notifications de l'utilisateur."""
    model = Notification
    template_name = 'notifications/notification_dropdown.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class UnreadCountView(LoginRequiredMixin, View):
    """Nombre de notifications non lues (AJAX)."""
    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({'count': count})


class MarkReadView(LoginRequiredMixin, View):
    """Marquer une notification comme lue."""
    def post(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, user=request.user)
            notif.is_read = True
            notif.save(update_fields=['is_read'])
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False}, status=404)


class MarkAllReadView(LoginRequiredMixin, View):
    """Marquer toutes les notifications comme lues."""
    def post(self, request):
        
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})