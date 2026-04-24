from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('<str:order_type>/<str:order_id>/', views.PaymentProcessView.as_view(), name='process'),
    path('initier/', views.InitiatePaymentView.as_view(), name='initiate'),
    path('attente/', views.PaymentWaitingView.as_view(), name='waiting'),
    path('verifier/', views.PaymentCheckView.as_view(), name='check'),
    path('succes/', views.PaymentSuccessView.as_view(), name='success'),
    path('echec/', views.PaymentFailureView.as_view(), name='failure'),
    path('webhook/mobile-money/', views.PaymentWebhookView.as_view(), name='webhook_mm'),
]