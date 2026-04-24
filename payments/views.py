import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone

from .models import Payment, TransactionLog
from .services import MobileMoneyService
import logging

logger = logging.getLogger(__name__)

class PaymentProcessView(LoginRequiredMixin, TemplateView):
    """Page de traitement du paiement."""
    template_name = 'payments/payment_process.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_type = kwargs.get('order_type')
        order_id = kwargs.get('order_id')
        user = self.request.user

        amount = 0
        description = ""

        if order_type == 'shop':
            from shop.models import Order
            order = get_object_or_404(Order, order_number=order_id, user=user)
            amount = order.total
            description = f"Commande CMD-{order.order_number}"

        elif order_type == 'pressing':
            from pressing.models import PressingOrder
            order = get_object_or_404(PressingOrder, order_number=order_id, user=user)
            amount = order.total
            description = f"Pressing PRS-{order.order_number}"

        elif order_type == 'fai':
            from fai.models import Subscription
            try:
                sub = Subscription.objects.get(id=int(order_id), foyer__subscriber=user)
                amount = sub.offer.price
                description = f"Internet - {sub.offer.name}"
            except (ValueError, Subscription.DoesNotExist):
                messages.error(self.request, "Abonnement introuvable.")
                return redirect('fai:offers')

        context['amount'] = amount
        context['description'] = description
        context['order_type'] = order_type
        context['order_id'] = order_id

        self.request.session['payment_pending'] = {
            'order_type': order_type,
            'order_id': order_id,
            'amount': str(amount),
        }
        return context


class InitiatePaymentView(LoginRequiredMixin, View):
    """Lancer un paiement Mobile Money."""
    def post(self, request):
        pending = request.session.get('payment_pending')
        if not pending:
            return redirect('pages:home')

        operator = request.POST.get('operator')  # tmoney ou flooz
        phone = request.POST.get('phone_number')

        if not phone or not operator:
            messages.error(request, "Veuillez remplir tous les champs.")
            return redirect('payments:process',
                            order_type=pending['order_type'],
                            order_id=pending['order_id'])

        # Créer le paiement en BDD
        payment = Payment.objects.create(
            user=request.user,
            order_type=pending['order_type'],
            order_id=pending['order_id'],
            amount=pending['amount'],
            method='mobile_money',
            operator=operator,
            phone_number=phone,
            status='pending',
        )

        TransactionLog.objects.create(
            payment=payment,
            event='initiated',
            payload={'operator': operator, 'phone': phone, 'amount': pending['amount']},
        )

        # Appeler le service Mobile Money
        mm_service = MobileMoneyService()
        result = mm_service.initiate(
            amount=float(pending['amount']),
            phone=phone,
            operator=operator,
            reference=f"DKP-{payment.payment_id}",
        )

        if result.get('success'):
            payment.external_ref = result.get('transaction_id', '')
            payment.status = 'processing'
            payment.save(update_fields=['external_ref', 'status'])

            TransactionLog.objects.create(
                payment=payment,
                event='callback_received',  # en réalité c'est juste la réponse immédiate
                payload=result,
            )

            request.session['last_payment_id'] = payment.payment_id
            return redirect('payments:waiting')
        else:
            payment.status = 'failed'
            payment.save(update_fields=['status'])
            TransactionLog.objects.create(
                payment=payment, event='failed', payload=result
            )
            messages.error(request, f"Erreur de paiement : {result.get('message', 'Erreur inconnue')}")
            return redirect('payments:process',
                            order_type=pending['order_type'],
                            order_id=pending['order_id'])


class PaymentWaitingView(LoginRequiredMixin, TemplateView):
    """Page d'attente du paiement (polling ou WebSocket)."""
    template_name = 'payments/payment_waiting.html'  # Assurez-vous que ce template existe


class PaymentCheckView(LoginRequiredMixin, View):
    """Vérifier le statut du paiement (AJAX polling)."""
    def get(self, request):
        payment_id = request.session.get('last_payment_id')
        if not payment_id:
            return JsonResponse({'status': 'not_found'})

        try:
            payment = Payment.objects.get(payment_id=payment_id, user=request.user)
            # Vérifier le statut auprès de l'opérateur
            if payment.status == 'processing' and payment.external_ref:
                mm_service = MobileMoneyService()
                result = mm_service.check_status(payment.external_ref)
                if result.get('status') == 'success':
                    payment.status = 'success'
                    payment.paid_at = timezone.now()
                    payment.save(update_fields=['status', 'paid_at'])
                    self._on_payment_success(payment)
                elif result.get('status') in ['failed', 'cancelled', 'expired']:
                    payment.status = 'failed'
                    payment.save(update_fields=['status'])

            return JsonResponse({'status': payment.status})
        except Payment.DoesNotExist:
            return JsonResponse({'status': 'not_found'})

    def _on_payment_success(self, payment):
        """Actions post-paiement réussi."""
        from notifications.services import NotificationService

        if payment.order_type == 'shop':
            from shop.models import Order
            order = Order.objects.filter(order_number=payment.order_id).first()
            if order:
                order.status = 'confirmed'
                order.save(update_fields=['status'])
                NotificationService.send(
                    user=payment.user,
                    type_notif='payment',
                    title="Paiement confirmé",
                    message=f"Votre commande CMD-{order.order_number} a été confirmée.",
                    link=f"/orders/{order.order_number}/tracking/"
                )

        elif payment.order_type == 'pressing':
            from pressing.models import PressingOrder
            order = PressingOrder.objects.filter(order_number=payment.order_id).first()
            if order:
                order.status = 'picked_up'
                order.save(update_fields=['status'])

        elif payment.order_type == 'fai':
            from fai.models import Subscription
            try:
                sub = Subscription.objects.get(id=int(payment.order_id))
                sub.status = 'active'
                sub.save(update_fields=['status'])
                if sub.offer.offer_type == 'ftth' and sub.foyer:
                    from fai.tasks import activate_onu_task
                    activate_onu_task.delay(sub.id)
            except (ValueError, Subscription.DoesNotExist):
                pass

        from .tasks import generate_receipt_pdf
        generate_receipt_pdf.delay(payment.payment_id)


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/payment_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment_id = self.request.session.get('last_payment_id')
        if payment_id:
            context['payment'] = get_object_or_404(Payment, payment_id=payment_id, user=self.request.user)
        return context


class PaymentFailureView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/payment_failure.html'


class PaymentWebhookView(View):
    """Endpoint callback Mobile Money (sans auth)."""
    def post(self, request):
        data = json.loads(request.body)
        # PayGateGlobal envoie 'identifier' et 'tx_reference' entre autres
        identifier = data.get('identifier', '')
        tx_reference = data.get('tx_reference', '')
        status_code = data.get('status')  # 0 = success

        try:
            # On peut chercher par external_ref (tx_reference) ou par reference dans identifier
            payment = Payment.objects.filter(external_ref=tx_reference).first()
            if not payment and identifier:
                # L'identifier contient notre référence "DKP-xxx"
                payment = Payment.objects.filter(payment_id=identifier.replace('DKP-', '')).first()

            if payment:
                TransactionLog.objects.create(
                    payment=payment,
                    event='webhook_received',
                    payload=data,
                )

                if status_code == 0:
                    payment.status = 'success'
                    payment.paid_at = timezone.now()
                    payment.save(update_fields=['status', 'paid_at'])
                    # Déclencher les actions post-paiement
                    PaymentCheckView()._on_payment_success(payment)
                else:
                    payment.status = 'failed'
                    payment.save(update_fields=['status'])

        except Exception as e:
            logger.exception("Erreur webhook")

        return JsonResponse({'status': 'ok'})