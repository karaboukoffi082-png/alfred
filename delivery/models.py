from django.db import models
from django.conf import settings


class DeliveryTracking(models.Model):
    """Suivi de livraison d'une commande."""
    STATUS_CHOICES = [
        ('preparing', 'Préparation en cours'),
        ('ready', 'Prêt pour envoi'),
        ('picked_up', 'Collecté par livreur'),
        ('in_transit', 'En transit'),
        ('nearby', 'Proche de la destination'),
        ('delivered', 'Livré'),
        ('failed', 'Échec de livraison'),
    ]

    order = models.OneToOneField('shop.Order', on_delete=models.CASCADE, related_name='delivery_tracking')
    driver_name = models.CharField(max_length=150, blank=True)
    driver_phone = models.CharField(max_length=20, blank=True)
    current_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='preparing')
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'delivery_tracking'
        verbose_name = 'Suivi de livraison'
        verbose_name_plural = 'Suivis de livraison'

    def __str__(self):
        return f"Livraison {self.order.order_number} - {self.get_current_status_display()}"


class DeliveryEvent(models.Model):
    """Événement de suivi (historique)."""
    tracking = models.ForeignKey(DeliveryTracking, on_delete=models.CASCADE, related_name='events')
    status = models.CharField(max_length=15, choices=DeliveryTracking.STATUS_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'delivery_events'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.tracking.order.order_number} - {self.get_status_display()}"