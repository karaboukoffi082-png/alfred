from django.db import models
from django.conf import settings
from django.utils.text import slugify


class PressingService(models.Model):
    """Services de pressing (Lavage, Repassage, Nettoyage à sec...)."""

    TYPE_CHOICES = [
        ('wash', 'Lavage'),
        ('iron', 'Repassage'),
        ('dry_clean', 'Nettoyage à sec'),
        ('wash_iron', 'Lavage + Repassage'),
        ('special', 'Traitement spécial'),
    ]

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    service_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)  # Augmenté pour les gros montants
    price_per_kg = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    turnaround_hours = models.PositiveIntegerField(default=48, help_text="Délai en heures")
    image = models.ImageField(upload_to='pressing/services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'pressing_services'
        verbose_name = 'Service pressing'
        verbose_name_plural = 'Services pressing'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while PressingService.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class PressingOrder(models.Model):
    """Commande pressing."""
    STATUS_CHOICES = [
        ('pending', 'En attente de prise en charge'),
        ('picked_up', 'Récupéré'),
        ('in_progress', 'En cours de traitement'),
        ('ready', 'Prêt'),
        ('delivered', 'Livré'),
        ('cancelled', 'Annulé'),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='pressing_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    pickup_address = models.ForeignKey('users.Address', on_delete=models.SET_NULL, null=True, blank=True, related_name='pressing_pickups')
    delivery_address = models.ForeignKey('users.Address', on_delete=models.SET_NULL, null=True, blank=True, related_name='pressing_deliveries')
    scheduled_date = models.DateTimeField(null=True, blank=True, help_text="Date de prise en charge souhaitée")
    total_weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Poids total en kg")
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)  # Jusqu'à 99 999 999 999,99 FCFA
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pressing_orders'
        verbose_name = 'Commande pressing'
        verbose_name_plural = 'Commandes pressing'
        ordering = ['-created_at']

    def __str__(self):
        return f"PRS-{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)


class PressingOrderItem(models.Model):
    """Ligne d'une commande pressing."""
    pressing_order = models.ForeignKey(PressingOrder, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(PressingService, on_delete=models.PROTECT)
    garment_description = models.CharField(max_length=200, help_text="Description du vêtement")
    quantity = models.PositiveIntegerField(default=1)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # Jusqu'à 999 999,99 kg
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)  # Jusqu'à 9 999 999 999,99 FCFA
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)    # Jusqu'à 99 999 999 999,99 FCFA

    class Meta:
        db_table = 'pressing_order_items'

    def __str__(self):
        return f"{self.garment_description} - {self.service.name}"

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        if self.weight_kg and self.service.price_per_kg:
            self.subtotal = self.service.price_per_kg * self.weight_kg * self.quantity
        super().save(*args, **kwargs)