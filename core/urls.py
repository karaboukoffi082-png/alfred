from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls', namespace='pages')),
    path('compte/', include('users.urls', namespace='users')),
    path('boutique/', include('shop.urls', namespace='shop')),
    path('pressing/', include('pressing.urls', namespace='pressing')),
    path('internet/', include('fai.urls', namespace='fai')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('paiement/', include('payments.urls', namespace='payments')),
    
    path('livraison/', include('delivery.urls', namespace='delivery')),
    path('inbox/notifications/', include('notifications.urls', namespace='notifications')),

]  

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)