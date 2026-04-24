from decimal import Decimal, DecimalException
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import PressingService, PressingOrder, PressingOrderItem
from .forms import PressingOrderForm


class ServicesView(ListView):
    """Liste des services pressing."""
    model = PressingService
    template_name = 'pressing/services.html'
    context_object_name = 'services'

    def get_queryset(self):
        return PressingService.objects.filter(is_active=True)


class ScheduleView(LoginRequiredMixin, TemplateView):
    """Prise de rendez-vous pressing."""
    template_name = 'pressing/schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = PressingService.objects.filter(is_active=True)
        context['addresses'] = self.request.user.addresses.all()
        context['form'] = PressingOrderForm(user=self.request.user)
        return context


class CreatePressingOrderView(LoginRequiredMixin, View):
    """Créer une commande pressing."""
    def post(self, request):
        service_id = request.POST.get('service')
        garment_desc = request.POST.get('garment_description')
        quantity_str = request.POST.get('quantity', '1')
        weight_str = request.POST.get('weight')
        scheduled = request.POST.get('scheduled_date')
        pickup_addr = request.POST.get('pickup_address')
        delivery_addr = request.POST.get('delivery_address')

        # Validation de la quantité
        try:
            quantity = int(quantity_str)
            if quantity < 1:
                raise ValueError("Quantité invalide")
        except ValueError:
            messages.error(request, "La quantité doit être un nombre entier positif.")
            return redirect('pressing:schedule')

        # Récupération du service
        try:
            service = PressingService.objects.get(id=service_id, is_active=True)
        except PressingService.DoesNotExist:
            messages.error(request, "Service invalide.")
            return redirect('pressing:schedule')

        # Calcul du prix unitaire
        weight_decimal = None
        try:
            if weight_str and service.price_per_kg:
                weight_decimal = Decimal(weight_str)
                unit_price = service.price_per_kg * weight_decimal
            else:
                unit_price = service.base_price
        except (ValueError, DecimalException):
            messages.error(request, "Le poids doit être un nombre valide.")
            return redirect('pressing:schedule')

        # Création de la commande
        order = PressingOrder.objects.create(
            user=request.user,
            scheduled_date=scheduled or None,
            total=unit_price * quantity,   # Decimal * int → Decimal
        )

        if pickup_addr:
            order.pickup_address_id = pickup_addr
        if delivery_addr:
            order.delivery_address_id = delivery_addr
        order.save()

        # Création de la ligne de commande
        PressingOrderItem.objects.create(
            pressing_order=order,
            service=service,
            garment_description=garment_desc,
            quantity=quantity,
            weight_kg=weight_decimal,   # déjà Decimal ou None
            unit_price=unit_price,
        )

        messages.success(request, f"Commande pressing PRS-{order.order_number} créée.")
        return redirect('payments:process', order_type='pressing', order_id=order.order_number)


class PressingTrackingView(LoginRequiredMixin, ListView):
    """Suivi des commandes pressing du client."""
    model = PressingOrder
    template_name = 'pressing/tracking.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return PressingOrder.objects.filter(
            user=self.request.user
        ).prefetch_related('items').order_by('-created_at')