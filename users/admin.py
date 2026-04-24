from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address

# --- ADMIN POUR USER ---
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Colonnes affichées dans la liste
    list_display = ('username', 'email', 'role', 'phone', 'is_verified', 'is_staff')
    
    # Filtres latéraux
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff')
    
    # Barre de recherche
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    
    # Organisation du formulaire d'édition (on ajoute nos champs personnalisés à ceux de base)
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('role', 'phone', 'avatar', 'is_verified')
        }),
    )


# --- ADMIN POUR ADDRESS ---
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('full_name', 'user', 'city', 'quartier', 'label', 'is_default')
    
    # Filtres latéraux
    list_filter = ('label', 'is_default')
    
    # Barre de recherche
    search_fields = ('full_name', 'street', 'city', 'user__username', 'user__email')
    
    # Optimisation: évite de faire des centaines de requêtes SQL pour afficher le nom d'utilisateur
    list_select_related = ('user',)