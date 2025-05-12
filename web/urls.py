from django.urls import path
from . import views # Intenta con esta línea
from .views import CompraListAPIView, CategoriaListAPIView



urlpatterns = [
path('', views.index, name='index'),
path('index', views.index, name='index'),
path('categorias/', views.listar_categorias, name='listar_categorias'),
path('categorias/nueva/', views.nueva_categoria, name='nueva_categoria'),
path('categorias/modificar/<int:id>/', views.modificar_categoria, name='modificar_categoria'),
path('categorias/eliminar/<int:id>/', views.eliminar_categoria, name='eliminar_categoria'),
path('productos/', views.listar_productos, name='productos'),
path('productos/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
path('productos/historial_compras/', views.historial_compras, name='historial_compras'),
path('productos/confirmar_compra/<int:compra_id>/', views.confirmar_compra, name='confirmar_compra'),
path('login/', views.login, name='login'),
path('api/compras/', CompraListAPIView.as_view(), name='compra-list'),
path('api/categorias/', CategoriaListAPIView.as_view(), name='categorias-list'),
]