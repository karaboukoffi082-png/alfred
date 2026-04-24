from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('connexion/', views.CustomLoginView.as_view(), name='login'),
    path('inscription/', views.RegisterView.as_view(), name='register'),
    path('deconnexion/', views.LogoutViewCustom.as_view(), name='logout'),
    path('mot-de-passe-oublie/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('mot-de-passe-oublie/fait/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('mot-de-passe-reinitialiser/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('mot-de-passe-reinitialiser/fait/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profil/', views.ProfileUpdateView.as_view(), name='profile'),
    path('tableau-de-bord/', views.ClientDashboardView.as_view(), name='dashboard'),
    path('adresse/ajouter/', views.AddressCreateView.as_view(), name='address_add'),
    path('adresse/<int:pk>/modifier/', views.AddressUpdateView.as_view(), name='address_edit'),
    path('adresse/<int:pk>/supprimer/', views.AddressDeleteView.as_view(), name='address_delete'),
]