from django.contrib import admin
from .models import DeliveryTracking, DeliveryEvent


# --- INLINE POUR DELIVERYEVENT ---
class DeliveryEventInline(admin.TabularInline):
    model = DeliveryEvent
    extra = 1
    readonly_fields = ('created_at',)
    fields = ('status', 'description', 'location', 'created_at')


# --- ADMIN POUR DELIVERYTRACKING ---
@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ('order', 'driver_name', 'driver_phone', 'current_status', 'estimated_delivery', 'created_at')
    list_filter = ('current_status',)
    search_fields = ('order__order_number', 'driver_name', 'driver_phone')
    list_select_related = ('order',)
    date_hierarchy = 'created_at'
    
    inlines = [DeliveryEventInline]
    
    readonly_fields = ('created_at', 'delivered_at')
    fieldsets = (
        ('Commande associée', {
            'fields': ('order',)
        }),
        ('Informations Livreur', {
            'fields': ('driver_name', 'driver_phone')
        }),
        ('Statut et Suivi', {
            'fields': ('current_status', 'estimated_delivery', 'delivered_at')
        }),
        ('Système', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )