from django.urls import path
from . import views # Intenta con esta línea



urlpatterns = [
path('', views.index, name='index'),
path('index', views.index, name='index'),
]