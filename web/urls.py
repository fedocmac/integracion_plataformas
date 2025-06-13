from django.urls import path
from . import views
from .views import CompraListAPIView, CategoriaListAPIView, proxy_login,registrar,proxy_register
from .views import logout_view

urlpatterns = [
    path('', views.login_view, name='root'),  # ← ahora “/” apunta al login
    path("index/", views.index, name="index"),
    path('login/', views.login_view, name='login'),  # ← Esto debe existir
    path("proxy-login", proxy_login),
    path('categorias/', views.listar_categorias, name='listar_categorias'),
    path('categorias/nueva/', views.nueva_categoria, name='nueva_categoria'),
    path('categorias/modificar/<int:id>/', views.modificar_categoria, name='modificar_categoria'),
    path('categorias/eliminar/<int:id>/', views.eliminar_categoria, name='eliminar_categoria'),
    path('productos/', views.listar_productos, name='productos'),
    path('productos/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('productos/historial_compras/', views.historial_compras, name='historial_compras'),
    path('productos/confirmar_compra/<int:compra_id>/', views.confirmar_compra, name='confirmar_compra'),
    path('api/compras/', CompraListAPIView.as_view(), name='compra-list'),
    path('api/categorias/', CategoriaListAPIView.as_view(), name='categorias-list'),
    path("registrar/", registrar, name="registrar"),  # URL accesible como /registrar/
    path("proxy-register", proxy_register),
    path("confirmar/", views.confirm_view, name="confirmar"),   
    path("logout/", logout_view, name="logout"),
    path("logout/", views.logout_view, name="logout"),
    path("logout/", logout_view, name="logout"),

]
