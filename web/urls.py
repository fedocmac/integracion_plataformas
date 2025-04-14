from django.urls import path
from . import views # Intenta con esta línea



urlpatterns = [
path('', views.index, name='index'),
path('index', views.index, name='index'),
path('categorias/', views.listar_categorias, name='listar_categorias'),
path('categorias/nueva', views.nueva_categoria, name='nueva_categoria'),
path('categorias/modificar/<int:id>/', views.modificar_categoria, name='modificar_categoria'),
path('categorias/eliminar/<int:id>/', views.eliminar_categoria, name='eliminar_categoria'),
path('login/', views.login, name='login'),
]