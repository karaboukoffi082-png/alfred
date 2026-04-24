from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from .models import ChatRoom, Message

User = get_user_model()


class InboxView(LoginRequiredMixin, ListView):
    """Liste des conversations."""
    model = ChatRoom
    template_name = 'chat/inbox.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user or user.is_support_user:
            return ChatRoom.objects.filter(is_closed=False)
        return ChatRoom.objects.filter(participant=user, is_closed=False)


class ChatRoomView(LoginRequiredMixin, TemplateView):
    """Salon de chat individuel."""
    template_name = 'chat/chat_room.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_id = kwargs.get('room_id')
        room = get_object_or_404(ChatRoom, room_id=room_id)

        # Vérifier accès
        user = self.request.user
        if not (user.is_admin_user or user.is_support_user or room.participant == user):
            from django.http import Http404
            raise Http404

        context['room'] = room
        context['messages'] = room.messages.select_related('sender')[:100]
        return context


class CreateOrGetRoomView(LoginRequiredMixin, TemplateView):
    """Créer ou récupérer un salon existant."""
    def get(self, request, room_type='support'):
        user = request.user
        room, created = ChatRoom.objects.get_or_create(
            participant=user,
            room_type=room_type,
            is_closed=False,
        )
        if created and room_type == 'support':
            # Assigner automatiquement à un agent support disponible
            support_user = User.objects.filter(
                role__in=[User.Role.ADMIN, User.Role.SUPPORT], is_active=True
            ).first()
            if support_user:
                room.assigned_to = support_user
                room.save(update_fields=['assigned_to'])
        return redirect('chat:room', room_id=room.room_id)