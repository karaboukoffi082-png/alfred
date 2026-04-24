from django.contrib import admin
from .models import Category, SubCategory, Product, Order, OrderItem, Review


# --- ADMIN POUR CATEGORY ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


# --- ADMIN POUR SUBCATEGORY ---
@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('category', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_select_related = ('category',)


# --- ADMIN POUR PRODUCT ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'old_price', 'stock', 'is_active', 'is_featured', 'is_organic')
    list_filter = ('category', 'subcategory', 'is_active', 'is_featured', 'is_organic', 'unit')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_select_related = ('category', 'subcategory')
    
    readonly_fields = (
        'rating_avg', 'review_count', 'discount_percent', 'in_stock', 
        'created_at', 'updated_at'
    )
    fieldsets = (
        (None, {
            'fields': ('category', 'subcategory', 'name', 'slug', 'description')
        }),
        ('Prix et Stock', {
            'fields': ('price', 'old_price', 'unit', 'stock', 'min_stock_alert')
        }),
        ('Médias', {
            'fields': ('image', 'images')
        }),
        ('Options et Statistiques', {
            'fields': ('is_active', 'is_featured', 'is_organic', 'rating_avg', 'review_count', 'discount_percent', 'in_stock'),
            'classes': ('collapse',) # Permet de replier cette section
        }),
    )


# --- INLINE POUR ORDERITEM ---
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'product_price', 'unit', 'quantity', 'subtotal')
    # On met tout en lecture seule pour éviter de casser la logique de calcul des totaux


# --- ADMIN POUR ORDER ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    date_hierarchy = 'created_at'
    list_select_related = ('user', 'address')
    
    inlines = [OrderItemInline]
    
    readonly_fields = (
        'order_number', 'subtotal', 'delivery_fee', 'total', 'created_at', 'updated_at'
    )
    fieldsets = (
        ('Informations Commande', {
            'fields': ('order_number', 'user', 'address', 'status', 'note')
        }),
        ('Facturation', {
            'fields': (('subtotal', 'delivery_fee'), 'total'),
            'classes': ('wide',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# --- ADMIN POUR REVIEW ---
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    list_editable = ('is_approved',)
    search_fields = ('product__name', 'user__username', 'comment')
    list_select_related = ('product', 'user')
    
    actions = ['approve_reviews']
    
    @admin.action(description='Approuver les avis sélectionnés')
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)