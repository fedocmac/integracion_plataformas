from django.urls import path
from django.views.generic import TemplateView
from django.shortcuts import redirect
from . import views

urlpatterns = [
    # Página raíz
    path('', lambda request: redirect('/login/'), name='root'),

    # Páginas HTML
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),  
    path('registrar/', TemplateView.as_view(template_name='registrar.html'), name='registrar_page'),
    path('confirmar/', TemplateView.as_view(template_name='confirmar.html'), name='confirmar_page'),
     path('index/',     TemplateView.as_view(template_name='index.html'),     name='index_page'),

    # Proxies a la API externa (usa los nombres reales)
    path('api/login/',    views.login_api,  name='api_login'),
    path('api/register/', views.registrar,  name='api_register'),
    path('api/confirm/',  views.confirmar,  name='api_confirm'),

    # Sesión e index
    path('logout/', views.logout_view, name='logout'),
    path('index/',  views.index,       name='index'),

    # Categorías
    path('categorias/',                       views.listar_categorias,   name='listar_categorias'),
    path('categorias/nueva/',                 views.nueva_categoria,     name='nueva_categoria'),
    path('categorias/modificar/<int:id>/',    views.modificar_categoria, name='modificar_categoria'),
    path('categorias/eliminar/<int:id>/',     views.eliminar_categoria,  name='eliminar_categoria'),

    # Productos y compras
    path('productos/',                                  views.listar_productos,  name='productos'),
    path('productos/<int:producto_id>/',                views.detalle_producto,  name='detalle_producto'),
    path('productos/historial_compras/',                views.historial_compras, name='historial_compras'),
    path('productos/confirmar_compra/<int:compra_id>/', views.confirmar_compra,  name='confirmar_compra'),

    # API REST (DRF)
    path('api/compras/',    views.CompraListAPIView.as_view(),    name='compra-list'),
    path('api/categorias/', views.CategoriaListAPIView.as_view(), name='categorias-list'),
]
