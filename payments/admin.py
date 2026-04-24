from django.contrib import admin
from .models import Payment, TransactionLog


# --- INLINE POUR TRANSACTIONLOG ---
class TransactionLogInline(admin.TabularInline):
    model = TransactionLog
    extra = 0
    can_delete = False
    readonly_fields = ('event', 'payload', 'response', 'created_at')
    # Les champs JSON sont mis en lecture seule car ils sont volumineux et techniques


# --- ADMIN POUR PAYMENT ---
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'order_type', 'order_id', 'amount', 'method', 'operator', 'status', 'created_at')
    list_filter = ('status', 'method', 'operator', 'order_type')
    search_fields = ('payment_id', 'user__username', 'user__email', 'order_id', 'external_ref', 'phone_number')
    list_select_related = ('user',)
    date_hierarchy = 'created_at'
    
    inlines = [TransactionLogInline]
    
    readonly_fields = ('payment_id', 'paid_at', 'created_at', 'updated_at')
    fieldsets = (
        ('Informations générales', {
            'fields': ('payment_id', 'user', 'order_type', 'order_id', 'amount', 'status')
        }),
        ('Méthode de paiement', {
            'fields': ('method', 'operator', 'phone_number')
        }),
        ('Référence et Reçu', {
            'fields': ('external_ref', 'receipt_url')
        }),
        ('Dates', {
            'fields': ('paid_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )