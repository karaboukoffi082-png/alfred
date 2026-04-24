from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.CatalogView.as_view(), name='catalog'),
    path('produit/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('produit/<slug:slug>/avis/', views.AddReviewView.as_view(), name='add_review'),
    path('panier/', views.CartView.as_view(), name='cart'),
    path('ajouter-au-panier/', views.AddToCartView.as_view(), name='add_to_cart'),  # ← sans paramètre
    path('panier/modifier/', views.UpdateCartView.as_view(), name='update_cart'),
    path('panier/supprimer/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('commande/', views.CheckoutView.as_view(), name='checkout'),
    path('panier/count/', views.CartCountView.as_view(), name='cart_count'),


    path('commande/valider/', views.PlaceOrderView.as_view(), name='place_order'),
    path('commande/succes/', views.OrderSuccessView.as_view(), name='order_success'),
    path('commande/<str:order_number>/suivi/', views.OrderTrackingView.as_view(), name='order_tracking'),
]   