from django.db import models
from django.conf import settings


class Foyer(models.Model):
    """Foyer / Abonné Internet."""
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('disconnected', 'Déconnecté'),
    ]

    subscriber = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='foyers')
    name = models.CharField(max_length=150, help_text="Nom du foyer")
    phone = models.CharField(max_length=20)
    address = models.TextField()
    quartier = models.CharField(max_length=100)
    city = models.CharField(max_length=100, default="Lomé")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fai_foyers'
        verbose_name = 'Foyer'
        verbose_name_plural = 'Foyers'

    def __str__(self):
        return f"{self.name} - {self.quartier}"


class Equipement(models.Model):
    """Équipements réseau (OLT, ONU, Splitter...)."""
    TYPE_CHOICES = [
        ('olt', 'OLT'),
        ('onu', 'ONU'),
        ('splitter', 'Splitter'),
        ('cable', 'Câble fibre'),
        ('other', 'Autre'),
    ]
    STATUS_CHOICES = [
        ('installed', 'Installé'),
        ('stock', 'En stock'),
        (' defective', 'Défectueux'),
        ('replaced', 'Remplacé'),
    ]

    type_eq = models.CharField(max_length=15, choices=TYPE_CHOICES, verbose_name="Type")
    serial_number = models.CharField(max_length=100, unique=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='stock')
    foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipements')
    installed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fai_equipements'
        verbose_name = 'Équipement'
        verbose_name_plural = 'Équipements'

    def __str__(self):
        return f"{self.get_type_eq_display()} - {self.serial_number}"


class DataOffer(models.Model):
    """Offres data Internet."""
    TYPE_CHOICES = [
        ('ftth', 'FTTH Fibre'),
        ('wifi', 'WiFi'),
        ('ticket', 'Ticket Data'),
    ]

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    offer_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    speed_mbps = models.PositiveIntegerField(help_text="Débit en Mbps")
    data_limit_gb = models.PositiveIntegerField(null=True, blank=True, help_text="Null = illimité")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    validity_days = models.PositiveIntegerField(default=30)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'fai_data_offers'
        verbose_name = 'Offre data'
        verbose_name_plural = 'Offres data'
        ordering = ['order', 'price']

    def __str__(self):
        return f"{self.name} - {self.speed_mbps}Mbps - {self.price} FCFA"

    @property
    def data_label(self):
        if self.data_limit_gb:
            return f"{self.data_limit_gb} Go"
        return "Illimité"


class Subscription(models.Model):
    """Abonnement actif d'un foyer à une offre."""
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé'),
    ]

    foyer = models.ForeignKey(Foyer, on_delete=models.PROTECT, related_name='subscriptions')
    offer = models.ForeignKey(DataOffer, on_delete=models.PROTECT)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fai_subscriptions'
        verbose_name = 'Abonnement'
        verbose_name_plural = 'Abonnements'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.foyer.name} > {self.offer.name}"

    @property
    def is_active(self):
        return self.status == 'active' and self.expires_at > timezone.now()