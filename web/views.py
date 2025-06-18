from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from django.contrib.auth.decorators import login_required
from .models import Categoria, Producto, Compra
from .forms import CategoriaForm
from .serializers import CompraSerializer, CategoriaSerializer
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from . import views
from .models import UsuarioRegistro
import requests
import json
from django.core.mail import send_mail  # ← Esto va arriba, entre tus imports
from django.conf import settings        # ← Esto también


import random
import string
from django.core.mail import send_mail

from .models import  UsuarioRegistro


import random
from django.core.mail import send_mail


# ---------- REGISTRO y CONFIRMACIÓN  (solo vía API externa, sin BD Django) ----------

import json, requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

API_BASE = "http://35.168.133.16:3000"          # ⇦ usa https:// si tu backend tiene SSL


@csrf_exempt                               # ← no usamos CSRF porque solo actuamos como proxy
def registrar(request):
    """Registra un usuario en la API externa /register."""
    if request.method != "POST":
        return JsonResponse({"message": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body)          # {"username":..,"password":.., ...}
    except ValueError:
        return JsonResponse({"message": "JSON inválido"}, status=400)

    try:
        r = requests.post(f"{API_BASE}/register", json=data, timeout=5)
        return JsonResponse(r.json(), status=r.status_code)
    except requests.RequestException:
        return JsonResponse({"message": "No se pudo conectar con la API externa."},
                            status=502)


@csrf_exempt
def confirmar(request):
    """Confirma el código enviado al correo → /Confirm."""
    if request.method != "POST":
        return JsonResponse({"message": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body)          # {"username":..,"code":..}
    except ValueError:
        return JsonResponse({"message": "JSON inválido"}, status=400)

    try:
        r = requests.post(f"{API_BASE}/Confirm", json=data, timeout=5)
        return JsonResponse(r.json(), status=r.status_code)
    except requests.RequestException:
        return JsonResponse({"message": "No se pudo conectar con la API externa."},
                            status=502)


@csrf_exempt
def login_api(request):
    if request.method != "POST":
        return JsonResponse({"message": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body)       # {"username": "...", "password": "..."}
    except ValueError:
        return JsonResponse({"message": "JSON inválido"}, status=400)

    try:
        r = requests.post(f"{API_BASE}/login", json=data, timeout=5)
        return JsonResponse(r.json(), status=r.status_code)
    except requests.RequestException:
        return JsonResponse({"message": "No se pudo conectar con la API externa."}, status=502)


def generar_codigo():
    return str(random.randint(100000, 999999))  # 6 dígitos



def index(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect("login")
    usuario = UsuarioRegistro.objects.get(pk=usuario_id)
    return render(request, "index.html", {"usuario": usuario})


def logout_view(request):
    request.session.flush()
    return redirect("login")


# ---------- Vistas generales ----------


def error_404_view(request, exception):
    return render(request, '404.html', status=404)


# ---------- Proxy login (Codespaces ↔ Backend externo sin HTTPS) ----------
@csrf_exempt
def proxy_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            r = requests.post("http://35.168.133.16:3000/login", json=data)
            return JsonResponse(r.json(), status=r.status_code)
        except Exception as e:
            return JsonResponse({"message": "Error al conectar con el backend"}, status=500)




@csrf_exempt
def proxy_register(request):
    if request.method == "POST":
        try:
            # Muestra el JSON recibido
            print("🟢 Datos recibidos:", request.body)

            data = json.loads(request.body)

            # Envía a API externa
            url = "http://35.168.133.16:3000/register"
            print(f"🔁 Enviando POST a {url} con:", data)
            response = requests.post(url, json=data)

            # Intenta decodificar la respuesta
            try:
                print("🔵 Respuesta API externa:", response.text)
                return JsonResponse(response.json(), status=response.status_code)
            except ValueError:
                return JsonResponse({"message": "Respuesta no válida del servidor externo"}, status=500)

        except Exception as e:
            print("❌ Excepción capturada:", e)
            return JsonResponse({"message": "Error interno del servidor."}, status=500)
    else:
        return JsonResponse({"message": "Método no permitido"}, status=405)

# ---------- API REST ----------
class CompraListAPIView(generics.ListCreateAPIView):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer


class CategoriaListAPIView(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


# ---------- Categorías ----------
def listar_categorias(request):
    busqueda = request.GET.get('q', '')
    categorias_list = Categoria.objects.filter(nombre__icontains=busqueda).order_by('nombre') if busqueda else Categoria.objects.all().order_by('nombre')

    paginator = Paginator(categorias_list, 10)
    page = request.GET.get('page')
    try:
        categorias = paginator.page(page)
    except PageNotAnInteger:
        categorias = paginator.page(1)
    except EmptyPage:
        categorias = paginator.page(paginator.num_pages)

    return render(request, 'categorias/categorias.html', {
        'categorias': categorias,
        'busqueda': busqueda
    })


def nueva_categoria(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            Categoria.objects.create(
                nombre=form.cleaned_data['nombre'],
                descripcion=form.cleaned_data['descripcion']
            )
            return redirect('listar_categorias')
    else:
        form = CategoriaForm()

    return render(request, 'categorias/nueva.html', {'form': form})


def modificar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('listar_categorias')
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, 'categorias/modificar.html', {
        'form': form,
        'categoria': categoria
    })


def eliminar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    categoria.delete()
    return redirect('listar_categorias')


# ---------- Productos y Compras ----------
@login_required
def listar_productos(request):
    busqueda = request.GET.get('q', '')
    productos_list = Producto.objects.filter(nombre__icontains=busqueda).order_by('nombre') if busqueda else Producto.objects.all().order_by('nombre')

    paginator = Paginator(productos_list, 10)
    page = request.GET.get('page')
    try:
        productos = paginator.page(page)
    except PageNotAnInteger:
        productos = paginator.page(1)
    except EmptyPage:
        productos = paginator.page(paginator.num_pages)

    return render(request, 'productos/productos.html', {
        'productos': productos,
        'busqueda': busqueda
    })


def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    if request.method == 'POST':
        compra = Compra.objects.create(producto=producto)
        return redirect('confirmar_compra', compra_id=compra.id)

    return render(request, 'productos/detalle_producto.html', {'producto': producto})


def confirmar_compra(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)
    producto = compra.producto

    return render(request, 'productos/confirmar_compra.html', {
        'producto': producto,
        'compra': compra
    })

@login_required
def historial_compras(request):
    compras_list = Compra.objects.all()
    paginator = Paginator(compras_list, 10)
    page = request.GET.get('page')
    try:
        compras = paginator.page(page)
    except PageNotAnInteger:
        compras = paginator.page(1)
    except EmptyPage:
        compras = paginator.page(paginator.num_pages)

    return render(request, 'productos/historial_compras.html', {'compras': compras})
