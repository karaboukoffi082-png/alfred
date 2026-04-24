from django.urls import path
from . import views

app_name = 'fai'

urlpatterns = [
    path('', views.OffersView.as_view(), name='offers'),
    path('acheter/', views.BuyTicketView.as_view(), name='buy_ticket'),
    path('acheter/valider/', views.ProcessTicketPurchaseView.as_view(), name='process_purchase'),
    path('mes-abonnements/', views.MySubscriptionsView.as_view(), name='my_subscriptions'),
    path('portail-captif/', views.CaptivePortalView.as_view(), name='captive_portal'),
]