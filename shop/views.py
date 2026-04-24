from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Avg, Count
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from decimal import Decimal   # ← AJOUTER CETTE LIGNE

from .models import Category, SubCategory, Product, Order, OrderItem, Review
from users.models import Address  # <-- AJOUT MANQUANT pour éviter une future erreur
from .forms import ReviewForm 

from django.http import JsonResponse
from django.views import View

from .models import Cart, CartItem
class CartCountView(View):
    def get(self, request):
        cart = request.session.get('cart', {})
        count = sum(cart.values())
        return JsonResponse({'cart_count': count})
class CatalogView(ListView):
    """Catalogue produits avec filtres."""
    model = Product
    template_name = 'shop/catalog.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related('category', 'subcategory')

        # Filtre catégorie
        cat_slug = self.request.GET.get('category')
        if cat_slug:
            qs = qs.filter(category__slug=cat_slug)

        # Filtre sous-catégorie
        sub_slug = self.request.GET.get('subcategory')
        if sub_slug:
            qs = qs.filter(subcategory__slug=sub_slug)

        # Filtre recherche
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )

        # Filtre prix min/max
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        if price_min:
            qs = qs.filter(price__gte=price_min)
        if price_max:
            qs = qs.filter(price__lte=price_max)

        # Tri
        sort = self.request.GET.get('sort', '-created_at')
        if sort in ('price', '-price', '-created_at', 'name', '-rating_avg'):
            qs = qs.order_by(sort)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['featured_products'] = Product.objects.filter(
            is_active=True, is_featured=True
        ).select_related('category')[:8]
        context['current_category'] = self.request.GET.get('category', '')
        context['current_subcategory'] = self.request.GET.get('subcategory', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        # Maintenir les filtres en GET
        context['filters'] = self.request.GET.dict()
         # Ajout des sous-catégories si une catégorie est sélectionnée
        cat_slug = context['current_category']
        if cat_slug:
            try:
               category = Category.objects.get(slug=cat_slug)
               context['subcategories'] = category.subcategories.filter(is_active=True)
            except Category.DoesNotExist:
                context['subcategories'] = []
        else:
            context['subcategories'] = []

        return context 


class ProductDetailView(DetailView):
    """Détail d'un produit."""
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category', 'subcategory')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['reviews'] = product.reviews.filter(is_approved=True).select_related('user')
        context['related_products'] = Product.objects.filter(
            category=product.category, is_active=True
        ).exclude(pk=product.pk)[:6]
        context['review_form'] = ReviewForm()
        return context


class AddReviewView(LoginRequiredMixin, View):
    """Ajouter ou mettre à jour un avis sur un produit."""
    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        form = ReviewForm(request.POST)
        
        if form.is_valid():
            # --- CORRECTION FINALE : update_or_create au lieu de save() ---
            review, created = Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'comment': form.cleaned_data['comment'],
                    'is_approved': False
                }
            )
            # -------------------------------------------------------------

            # Mettre à jour la note moyenne
            avg = product.reviews.filter(is_approved=True).aggregate(a=Avg('rating'))['a'] or 0
            count = product.reviews.filter(is_approved=True).count()
            product.rating_avg = avg
            product.review_count = count
            product.save(update_fields=['rating_avg', 'review_count'])
            
            if created:
                messages.success(request, "Votre avis a été soumis et sera visible après validation.")
            else:
                messages.success(request, "Votre avis a été mis à jour avec succès.")
                
        return redirect(product.get_absolute_url())


class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', {})
        product_ids = cart.keys()
        products = Product.objects.filter(id__in=product_ids, is_active=True)
        cart_items = []
        subtotal = Decimal(0)
        for p in products:
            qty = cart[str(p.id)]
            item_subtotal = p.price * qty
            subtotal += item_subtotal
            cart_items.append({
                'product': p,
                'quantity': qty,
                'subtotal': item_subtotal,
            })
        delivery_fee = Decimal(500)
        total = subtotal + delivery_fee

        context['cart_items'] = cart_items
        context['cart_subtotal'] = subtotal
        context['delivery_fee'] = delivery_fee
        context['cart_total'] = total
        context['cart_count'] = sum(cart.values())
        return context
class AddToCartView(View):
    """Ajouter un produit au panier via session."""
    def post(self, request):
        import json
        
        # On lit les données envoyées en JSON par le JavaScript
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Données invalides'}, status=400)

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Produit introuvable'}, status=404)

        cart = request.session.get('cart', {})
        cart[str(product.id)] = cart.get(str(product.id), 0) + quantity
        request.session['cart'] = cart

        return JsonResponse({
            'success': True,
            'cart_count': sum(cart.values()),
            'message': f"{product.name} ajouté au panier"
        })

class UpdateCartView(View):
    """Mettre à jour quantité panier."""
    def post(self, request):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 0))
        cart = request.session.get('cart', {})

        if quantity <= 0:
            cart.pop(str(product_id), None)
        else:
            cart[str(product_id)] = quantity

        request.session['cart'] = cart
        return JsonResponse({'success': True, 'cart_count': sum(cart.values())})


class RemoveFromCartView(View):
    """Supprimer un produit du panier."""
    def post(self, request):
        product_id = request.POST.get('product_id')
        cart = request.session.get('cart', {})
        cart.pop(str(product_id), None)
        request.session['cart'] = cart
        return JsonResponse({'success': True, 'cart_count': sum(cart.values())})


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        cart = self.request.session.get('cart', {})

        if not cart:
            return redirect('shop:cart')

        product_ids = cart.keys()
        products = Product.objects.filter(id__in=product_ids, is_active=True)
        cart_items = []
        subtotal = Decimal(0)
        for p in products:
            qty = cart[str(p.id)]
            item_subtotal = p.price * qty
            subtotal += item_subtotal
            cart_items.append({'product': p, 'quantity': qty, 'subtotal': item_subtotal})

        delivery_fee = Decimal(500)
        total = subtotal + delivery_fee

        context['cart_items'] = cart_items
        context['subtotal'] = subtotal
        context['delivery_fee'] = delivery_fee
        context['total'] = total
        context['addresses'] = user.addresses.all()

        # Sauvegarde session pour la commande
        self.request.session['checkout_data'] = {
            'subtotal': str(subtotal),
            'delivery_fee': str(delivery_fee),
            'total': str(total),
        }
        return context


class PlaceOrderView(LoginRequiredMixin, View):
    def post(self, request):
        from payments.models import Payment

        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "Votre panier est vide.")
            return redirect('shop:cart')

        checkout_data = request.session.get('checkout_data', {})
        address_id = request.POST.get('address')

        # Vérification adresse
        try:
            address = request.user.addresses.get(id=address_id)
        except Address.DoesNotExist:
            messages.error(request, "Veuillez sélectionner une adresse de livraison valide.")
            return redirect('shop:checkout')

        # Création commande
        order = Order.objects.create(
            user=request.user,
            address=address,
            subtotal=checkout_data.get('subtotal', 0),
            delivery_fee=checkout_data.get('delivery_fee', 0),
            total=checkout_data.get('total', 0),
            note=request.POST.get('note', ''),
        )

        # Lignes de commande
        products = Product.objects.filter(id__in=cart.keys())
        for p in products:
            qty = cart[str(p.id)]
            OrderItem.objects.create(
                order=order,
                product=p,
                product_name=p.name,
                product_price=p.price,
                quantity=qty,
                unit=p.unit,
            )
            # Mise à jour stock
            p.stock = max(0, p.stock - qty)
            p.save(update_fields=['stock'])

        # Vider panier
        request.session['cart'] = {}
        request.session['last_order_id'] = order.id

        return redirect('payments:process', order_type='shop', order_id=order.order_number)


class OrderSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/order_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.request.session.get('last_order_id')
        if order_id:
            context['order'] = get_object_or_404(Order, id=order_id, user=self.request.user)
        return context


class OrderTrackingView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'delivery/tracking_detail.html'
    context_object_name = 'order'
    slug_url_kwarg = 'order_number'
    slug_field = 'order_number'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related(
            'address', 'delivery_tracking'
        ).prefetch_related('items')

class OrderSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/order_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.request.session.get('last_order_id')
        if order_id:
            context['order'] = get_object_or_404(Order, id=order_id, user=self.request.user)
        return context


class OrderTrackingView(LoginRequiredMixin, DetailView):
    """Suivi de commande client."""
    model = Order
    template_name = 'delivery/tracking_detail.html'
    context_object_name = 'order'
    slug_url_kwarg = 'order_number'
    slug_field = 'order_number'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related(
            'address', 'delivery_tracking'
        ).prefetch_related('items')