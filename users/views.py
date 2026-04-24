from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView,
    PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView, CreateView, UpdateView, DetailView, ListView
)
from django.urls import reverse_lazy
from django.contrib import messages

from .models import User, Address
from .forms import (
    CustomLoginForm, CustomUserCreationForm,
    UserProfileForm, AddressForm
)


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'users/login.html'

    def form_valid(self, form):
        messages.success(self.request, f"Bienvenue {form.get_user().get_full_name() or form.get_user().username} !")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Identifiants incorrects. Veuillez réessayer.")
        return super().form_invalid(form)


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = User.Role.CLIENT
        user.save()
        messages.success(self.request, "Compte créé avec succès. Connectez-vous.")
        return super().form_valid(form)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['addresses'] = Address.objects.filter(user=self.request.user)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profil mis à jour.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('users:profile')


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    form_class = AddressForm
    template_name = 'users/address_form.html'   # ← NOUVEAU TEMPLATE

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Adresse ajoutée avec succès.")
        return super().form_valid(form)

    def get_success_url(self):
        # Redirige vers le checkout si on vient de là, sinon vers le profil
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('users:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Passe le paramètre 'next' dans le contexte pour le réutiliser dans le formulaire si besoin
        context['next'] = self.request.GET.get('next', '')
        return context


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'users/address_form.html'   # ← NOUVEAU TEMPLATE

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Adresse modifiée avec succès.")
        return super().form_valid(form)

    def get_success_url(self):
        # Même logique de redirection
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('users:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '')
        return context


class AddressDeleteView(LoginRequiredMixin, TemplateView):
    """Suppression d'adresse via POST."""
    template_name = 'users/profile.html'

    def post(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        address.delete()
        messages.success(request, "Adresse supprimée.")
        return redirect('users:profile')


class ClientDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        from shop.models import Order
        from pressing.models import PressingOrder
        from fai.models import Subscription

        context['recent_orders'] = Order.objects.filter(user=user).order_by('-created_at')[:5]
        context['recent_pressing'] = PressingOrder.objects.filter(user=user).order_by('-created_at')[:5]
        context['active_subscriptions'] = Subscription.objects.filter(
            foyer__subscriber=user, status='active'
        ).order_by('-created_at')[:3]
        
        # Notifications : gérer le cas où la relation n'existe pas
        if hasattr(user, 'notifications'):
            context['unread_notifications'] = user.notifications.filter(is_read=False)[:10]
        else:
            context['unread_notifications'] = []
        
        return context


class LogoutViewCustom(LogoutView):
    next_page = reverse_lazy('pages:home')