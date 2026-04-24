from django.urls import path
from . import views

app_name = 'pressing'

urlpatterns = [
    path('', views.ServicesView.as_view(), name='services'),
    path('rendez-vous/', views.ScheduleView.as_view(), name='schedule'),
    path('commander/', views.CreatePressingOrderView.as_view(), name='create_order'),
    path('suivi/', views.PressingTrackingView.as_view(), name='tracking'),
]