from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.InboxView.as_view(), name='inbox'),
    path('demarrer/<str:room_type>/', views.CreateOrGetRoomView.as_view(), name='start'),
    path('<str:room_id>/', views.ChatRoomView.as_view(), name='room'),
]