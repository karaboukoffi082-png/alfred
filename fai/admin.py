from django.contrib import admin
from .models import Foyer, Equipement, DataOffer, Subscription


# --- ADMIN POUR FOYER ---
@admin.register(Foyer)
class FoyerAdmin(admin.ModelAdmin):
    list_display = ('name', 'subscriber', 'phone', 'quartier', 'city', 'status', 'created_at')
    list_filter = ('status', 'city')
    search_fields = ('name', 'quartier', 'subscriber__username', 'subscriber__phone')
    list_select_related = ('subscriber',)


# --- ADMIN POUR EQUIPEMENT ---
@admin.register(Equipement)
class EquipementAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'type_eq', 'brand', 'model', 'status', 'foyer', 'installed_at')
    list_filter = ('type_eq', 'status')
    search_fields = ('serial_number', 'brand', 'model', 'foyer__name')
    list_select_related = ('foyer',)
    
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('type_eq', 'serial_number', 'brand', 'model', 'status')
        }),
        ('Affectation', {
            'fields': ('foyer', 'installed_at')
        }),
        ('Divers', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )


# --- ADMIN POUR DATAOFFER ---
@admin.register(DataOffer)
class DataOfferAdmin(admin.ModelAdmin):
    list_display = ('name', 'offer_type', 'speed_mbps', 'data_label', 'price', 'validity_days', 'is_active', 'is_popular', 'order')
    list_editable = ('is_active', 'is_popular', 'order')
    list_filter = ('offer_type', 'is_active', 'is_popular')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    readonly_fields = ('data_label',)
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'offer_type', 'description')
        }),
        ('Caractéristiques', {
            'fields': ('speed_mbps', 'data_limit_gb', 'data_label', 'validity_days')
        }),
        ('Tarification et Mise en avant', {
            'fields': ('price', 'is_active', 'is_popular', 'order')
        }),
    )


# --- ADMIN POUR SUBSCRIPTION ---
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('foyer', 'offer', 'status', 'started_at', 'expires_at', 'auto_renew')
    list_filter = ('status', 'auto_renew')
    search_fields = ('foyer__name', 'offer__name')
    list_select_related = ('foyer', 'offer')
    date_hierarchy = 'started_at'
    
    readonly_fields = ('started_at', 'created_at', 'is_active')
    fieldsets = (
        (None, {
            'fields': ('foyer', 'offer', 'status')
        }),
        ('Durée', {
            'fields': ('started_at', 'expires_at', 'auto_renew')
        }),
        ('Informations système', {
            'fields': ('created_at', 'is_active'),
            'classes': ('collapse',)
        }),
    )