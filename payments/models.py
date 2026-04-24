from django.db import models
from django.conf import settings


class Payment(models.Model):
    """Paiement unique pour tout type de commande."""
    METHOD_CHOICES = [
        ('mobile_money', 'Mobile Money'),
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
    ]
    OPERATOR_CHOICES = [
        ('tmoney', 'T-Money'),
        ('flooz', 'Flooz'),
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
    ]
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('success', 'Réussi'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]
    ORDER_TYPE_CHOICES = [
        ('shop', 'Commande Boutique'),
        ('pressing', 'Commande Pressing'),
        ('fai', 'Abonnement Internet'),
    ]

    payment_id = models.CharField(max_length=30, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='payments')
    order_type = models.CharField(max_length=15, choices=ORDER_TYPE_CHOICES)
    order_id = models.CharField(max_length=20, help_text="ID de la commande source (CMD-xxx, PRS-xxx, etc.)")
    amount = models.DecimalField(max_digits=14, decimal_places=2)  # Jusqu'à 99 999 999 999,99 FCFA
    method = models.CharField(max_length=15, choices=METHOD_CHOICES)
    operator = models.CharField(max_length=15, choices=OPERATOR_CHOICES, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    external_ref = models.CharField(max_length=200, blank=True, help_text="Référence retour opérateur")
    receipt_url = models.FileField(upload_to='receipts/', blank=True, null=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_type', 'order_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"PAY-{self.payment_id} ({self.amount} FCFA)"

    def save(self, *args, **kwargs):
        if not self.payment_id:
            import uuid
            self.payment_id = uuid.uuid4().hex[:14].upper()
        super().save(*args, **kwargs)


class TransactionLog(models.Model):
    """Journal des transactions pour audit."""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='logs')
    event = models.CharField(max_length=50, help_text="initiated, callback_received, verified, failed")
    payload = models.JSONField(default=dict)
    response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transaction_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"LOG-{self.payment.payment_id} {self.event}"