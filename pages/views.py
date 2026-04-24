from django.views.generic import TemplateView
from shop.models import Product
from pressing.models import PressingService
from fai.models import DataOffer


class HomeView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(
            is_active=True, is_featured=True
        ).select_related('category')[:12]
        context['pressing_services'] = PressingService.objects.filter(is_active=True)[:4]
        context['internet_offers'] = DataOffer.objects.filter(
            is_active=True, is_popular=True
        )[:3]
        context['categories'] = Product.CATEGORY.objects.filter(is_active=True) if hasattr(Product, 'CATEGORY') else []
        return context


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class ContactView(TemplateView):
    template_name = 'pages/contact.html'


class FAQView(TemplateView):
    template_name = 'pages/faq.html'


class LegalView(TemplateView):
    template_name = 'pages/legal.html'