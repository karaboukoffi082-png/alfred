from django.contrib import admin
from .models import PressingService, PressingOrder, PressingOrderItem


# --- INLINE POUR PRESSINGORDERITEM ---
class PressingOrderItemInline(admin.TabularInline):
    model = PressingOrderItem
    extra = 0
    readonly_fields = ('service', 'garment_description', 'quantity', 'weight_kg', 'unit_price', 'subtotal')
    # Tout en lecture seule pour ne pas casser la logique de calcul du save()


# --- ADMIN POUR PRESSINGSERVICE ---
@admin.register(PressingService)
class PressingServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'base_price', 'price_per_kg', 'turnaround_hours', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('service_type', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


# --- ADMIN POUR PRESSINGORDER ---
@admin.register(PressingOrder)
class PressingOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_weight', 'total', 'scheduled_date', 'created_at')
    list_filter = ('status', 'created_at', 'scheduled_date')
    search_fields = ('order_number', 'user__username', 'user__email', 'note')
    date_hierarchy = 'created_at'
    list_select_related = ('user', 'pickup_address', 'delivery_address')
    
    inlines = [PressingOrderItemInline]
    
    readonly_fields = ('order_number', 'total_weight', 'total', 'created_at', 'updated_at')
    fieldsets = (
        ('Informations Commande', {
            'fields': ('order_number', 'user', 'status', 'note')
        }),
        ('Adresses et Logistique', {
            'fields': ('pickup_address', 'delivery_address', 'scheduled_date')
        }),
        ('Facturation', {
            'fields': ('total_weight', 'total'),
            'classes': ('wide',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )