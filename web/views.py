from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics

from .models import Categoria, Producto, Compra
from .forms import CategoriaForm
from .serializers import CompraSerializer, CategoriaSerializer

import requests
import json


# ---------- Vistas generales ----------
def index(request):
    return HttpResponse("Hola desde la vista index de la app web.")


def login(request):
    return render(request, 'login.html')  # Página con formulario de login


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

def registrar(request):
    return render(request, "registrar.html")  # tu archivo se llama así
