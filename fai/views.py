from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import DataOffer, Foyer, Subscription


class OffersView(ListView):
    """Offres Internet disponibles."""
    model = DataOffer
    template_name = 'fai/offers.html'
    context_object_name = 'offers'

    def get_queryset(self):
        return DataOffer.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_offers'] = DataOffer.objects.filter(
            is_active=True, is_popular=True
        )
        return context


class BuyTicketView(LoginRequiredMixin, TemplateView):
    """Achat de ticket data."""
    template_name = 'fai/buy_ticket.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offer_type = self.request.GET.get('type', 'ticket')
        context['offers'] = DataOffer.objects.filter(
            is_active=True, offer_type=offer_type
        )
        context['foyers'] = Foyer.objects.filter(
            subscriber=self.request.user, status='active'
        )
        return context


class ProcessTicketPurchaseView(LoginRequiredMixin, View):
    """Traiter l'achat d'un ticket/abonnement."""
    def post(self, request):
        offer_id = request.POST.get('offer')
        foyer_id = request.POST.get('foyer')

        try:
            offer = DataOffer.objects.get(id=offer_id, is_active=True)
        except DataOffer.DoesNotExist:
            messages.error(request, "Offre invalide.")
            return redirect('fai:buy_ticket')

        foyer = None
        if offer.offer_type == 'ftth':
            if not foyer_id:
                messages.error(request, "Sélectionnez un foyer pour l'abonnement FTTH.")
                return redirect('fai:buy_ticket')
            try:
                foyer = Foyer.objects.get(id=foyer_id, subscriber=request.user)
            except Foyer.DoesNotExist:
                messages.error(request, "Foyer invalide.")
                return redirect('fai:buy_ticket')

        # Créer l'abonnement
        expires = timezone.now() + timedelta(days=offer.validity_days)
        sub = Subscription.objects.create(
            foyer=foyer,
            offer=offer,
            expires_at=expires,
        )

        # Rediriger vers paiement
        return redirect('payments:process', order_type='fai', order_id=str(sub.id))


class MySubscriptionsView(LoginRequiredMixin, TemplateView):
    """Abonnements Internet du client."""
    template_name = 'fai/my_subscriptions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        foyers = Foyer.objects.filter(subscriber=self.request.user)
        context['foyers'] = foyers
        context['subscriptions'] = Subscription.objects.filter(
            foyer__in=foyers
        ).select_related('offer', 'foyer').order_by('-created_at')
        return context


class CaptivePortalView(TemplateView):
    """Portail captif WiFi (HORS base.html - page autonome pour routeurs)."""
    template_name = 'fai/captive_portal.html'