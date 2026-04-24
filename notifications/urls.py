from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('non-lues/', views.UnreadCountView.as_view(), name='unread_count'),
    path('<int:pk>/lue/', views.MarkReadView.as_view(), name='mark_read'),
    path('tout-lire/', views.MarkAllReadView.as_view(), name='mark_all_read'),
]