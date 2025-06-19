from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CategoriaForm
from .models import Categoria, Producto, Compra
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied
from rest_framework import generics
from .serializers import CompraSerializer, CategoriaSerializer
import requests
import json
from pathlib import Path
from django.conf import settings
from django.http import Http404
import jwt
from datetime import datetime, timezone

# Create your views here.
def index(request):
    
    if not check_login(request):
        return redirect('/login')
    
    user_info = get_user_info(request)
    if not user_info:
        return redirect('/login')  # No logeado

    username = user_info.get('name')  # o 'email' o 'sub'

    
    return render(request, 'index.html', {
        'username': username,   # Nombre del usuario logueado      
    })

class CompraListAPIView(generics.ListCreateAPIView):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer

class CategoriaListAPIView(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


def check_login(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return False

    try:
        payload = jwt.decode(access_token, options={"verify_signature": False})
        exp_timestamp = payload.get('exp')
        if not exp_timestamp:
            return False
        exp = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        if exp < datetime.now(tz=timezone.utc):
            return False
        return True
    except Exception:
        return False

def historial_compras(request):
    if not check_login(request):
        return redirect('/login')

    compras_list = Compra.objects.all()

    base_dir = Path(settings.BASE_DIR) / 'datos'
    archivo_productos = base_dir / 'products.json'

    productos = []
    if archivo_productos.exists():
        with open(archivo_productos, 'r', encoding='utf-8') as f:
            productos = json.load(f)

    productos_dict = {p['id']: p['name'] for p in productos}

    paginator = Paginator(compras_list, 10)
    page = request.GET.get('page')

    try:
        compras_page = paginator.page(page)
    except PageNotAnInteger:
        compras_page = paginator.page(1)
    except EmptyPage:
        compras_page = paginator.page(paginator.num_pages)

    # Crear lista enriquecida para el template
    compras_enriquecidas = []
    for compra in compras_page:
    
        
        compras_enriquecidas.append({
            'compra': compra,
            'producto_name': productos_dict.get(compra.producto_id, 'Producto no encontrado')
        })

    return render(request, 'productos/historial_compras.html', {
        'compras': compras_enriquecidas,
        'page_obj': compras_page  # si quieres paginación en template
    })

def confirmar_compra(request, compra_id):
    
    if not check_login(request):
        return redirect('/login')
    
    compra = get_object_or_404(Compra, pk=compra_id)
    producto_id = compra.producto_id  # El producto relacionado con la compra
    
    
    base_dir = Path(settings.BASE_DIR) / 'datos'
    archivo_productos = base_dir / 'products.json'
    
    if archivo_productos.exists():
        with open(archivo_productos, 'r', encoding='utf-8') as f:
            productos = json.load(f)
            
    dict_productos = {prod['id']: prod for prod in productos}
    
    producto = dict_productos.get(producto_id)

    return render(request, 'productos/confirmar_compra.html', {
        'producto': producto,
        'compra': compra
    })

def detalle_producto(request, producto_id):
    
    if not check_login(request):
        return redirect('/login')
    
    base_dir = Path(settings.BASE_DIR) / 'datos'
    archivo_productos = base_dir / 'products.json'
    archivo_categorias = base_dir / 'category.json'
    archivo_inventario = base_dir / 'inventory.json'
    
    productos = []
    categorias = []
    inventarios = []
    
    if archivo_productos.exists():
        with open(archivo_productos, 'r', encoding='utf-8') as f:
            productos = json.load(f)
    if archivo_categorias.exists():
        with open(archivo_categorias, 'r', encoding='utf-8') as f:
            categorias = json.load(f)
    if archivo_inventario.exists():
        with open(archivo_inventario, 'r', encoding='utf-8') as f:
            inventarios = json.load(f)
    
    dict_productos = {prod['id']: prod for prod in productos}
    dict_categorias = {cat['id']: cat for cat in categorias}
    dict_inventarios = {inv['productId']: inv for inv in inventarios}

    # Buscar el producto solicitado
    producto = dict_productos.get(producto_id)
    if not producto:
        raise Http404("Producto no encontrado")

    # Agregar info de categoría y stock
    cat_id = producto.get('categoryId')
    categoria = dict_categorias.get(cat_id, {}).get('name', 'Sin categoría')
    
    inventario = dict_inventarios.get(producto_id, {})
    stock = inventario.get('quantity', 0)
    minStock = inventario.get('minStock', 0)
    
    precio = dict_productos.get(producto_id, {}).get('price', 0)
    
    producto['categoria_nombre'] = categoria
    producto['stock'] = stock
    producto['minStock'] = minStock
 
    if request.method == 'POST':
        
        cantidad = int(request.POST.get('cantidad', 1))  # Por defecto, 1 si no viene nada

        # Validar rango permitido
        if cantidad < 1:
            cantidad = 1
        elif cantidad > 100:
            cantidad = 100
        
        api_base_url = "https://integracionstock-etefhkhbcadegaej.brazilsouth-01.azurewebsites.net/inventory"

        try:
            # 1. Obtener el inventario actual desde la API
            response = requests.get(api_base_url, params={"productId": producto_id})
            response.raise_for_status()
            
            inventarios_api = response.json()
            if not inventarios_api:
                raise Http404("Inventario no encontrado en la API")
            inventario = inventarios_api[0]  # Tomamos el primer (y único) resultado

            # 2. Crear nuevo payload para PUT
            updated_data = {
                "productId": inventario['productId'],
                "quantity": inventario['quantity'] + cantidad,
                "minStock": inventario['minStock'],
                "location": inventario['location'],
                "lastUpdated": inventario['lastUpdated']
            }

            # 3. Hacer el PUT con la información actualizada
            put_response = requests.put(api_base_url, json=updated_data)
            put_response.raise_for_status()
            
            compra = Compra.objects.create(
                producto_id=producto_id,
                cantidad=cantidad,
                precio_compra=precio*cantidad
            )

        except requests.RequestException as e:
            return HttpResponse(f"Error comunicándose con la API: {e}", status=500)

        return redirect('confirmar_compra', compra_id=compra.id)

    return render(request, 'productos/detalle_producto.html', {
        'producto': producto
    })
    

def listar_productos(request):
    
    if not check_login(request):
        return redirect('/login')
    
    busqueda = request.GET.get('q', '').lower()
    
    base_dir = Path(settings.BASE_DIR) / 'datos'
    
    # Cargar archivos JSON
    productos = []
    categorias = []
    inventarios = []
    
    archivo_productos = base_dir / 'products.json'
    archivo_categorias = base_dir / 'category.json'
    archivo_inventario = base_dir / 'inventory.json'
    
    if archivo_productos.exists():
        with open(archivo_productos, 'r', encoding='utf-8') as f:
            productos = json.load(f)
    if archivo_categorias.exists():
        with open(archivo_categorias, 'r', encoding='utf-8') as f:
            categorias = json.load(f)
    if archivo_inventario.exists():
        with open(archivo_inventario, 'r', encoding='utf-8') as f:
            inventarios = json.load(f)

    # Crear diccionarios para acceso rápido
    dict_categorias = {cat['id']: cat for cat in categorias}
    dict_inventarios = {inv['productId']: inv for inv in inventarios}

    # Filtrar productos por búsqueda y enriquecer con categoría y stock
    productos_filtrados = []
    for prod in productos:
        nombre = prod.get('name', '').lower()
        if busqueda in nombre:
            # Agregar categoría
            cat_id = prod.get('categoryId')
            categoria = dict_categorias.get(cat_id, {}).get('name', 'Sin categoría')
            
            # Agregar stock
            prod_id = prod.get('id')
            
            inventario = dict_inventarios.get(prod_id, {})
            stock = inventario.get("quantity", 0)
            minStock = inventario.get("minStock", 0)

            nuevo_prod = prod.copy()
            nuevo_prod['category'] = categoria
            nuevo_prod['stock'] = stock
            nuevo_prod['minStock'] = minStock

            productos_filtrados.append(nuevo_prod)

    # Ordenar por nombre
    #productos_filtrados = sorted(productos_filtrados, key=lambda x: x.get('name', '').lower())

    # Paginación
    paginator = Paginator(productos_filtrados, 8)
    page = request.GET.get('page')

    try:
        productos_paginados = paginator.page(page)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)

    return render(request, 'productos/productos.html', {
        'productos': productos_paginados,
        'busqueda': busqueda,
    })

def productos(request):
    
    if not check_login(request):
        return redirect('/login')
    
    return render(request, 'productos/productos.html')
    
    
"""def listar_productos(request):
    busqueda = request.GET.get('q', '')

    try:
        # 1. Obtener todos los productos
        productos_res = requests.get('https://integracionstock-etefhkhbcadegaej.brazilsouth-01.azurewebsites.net/products')
        productos_data = productos_res.json()
        
        print("Productos obtenidos:", len(productos_data), "productos")
        
    except Exception as e:
        print("Error al consumir productos:", e)
        productos_data = []

    # 2. Filtrar por búsqueda local (por nombre, si existe)
    if busqueda:
        productos_data = [p for p in productos_data if busqueda.lower() in p.get('name', '').lower()]

    productos_completos = []

    for producto in productos_data:
        producto_id = producto.get('id')
        categoria_id = producto.get('categoryId')

        # Obtener inventario
        try:
            inv_res = requests.get(f'https://integracionstock-etefhkhbcadegaej.brazilsouth-01.azurewebsites.net/inventory/{producto_id}')
            inventario = inv_res.json()
        except Exception as e:
            print(f"Error al obtener inventario del producto {producto_id}:", e)
            inventario = {}

        # Obtener categoría
        try:
            cat_res = requests.get(f'https://integracionstock-etefhkhbcadegaej.brazilsouth-01.azurewebsites.net/product-category/{categoria_id}')
            categoria = cat_res.json()
        except Exception as e:
            print(f"Error al obtener categoría del producto {producto_id}:", e)
            categoria = {}

        # Combinar en un solo objeto
        producto_completo = {
            'id': producto.get('id'),
            'sku': producto.get('sku'),
            'nombre': producto.get('name'),
            'descripcion': producto.get('description'),
            'precio': producto.get('price'),
            'costo': producto.get('cost'),
            'stock': inventario.get('quantity', 'N/D'),
            'min_stock': inventario.get('minStock', 'N/D'),
            'ubicacion': inventario.get('location', ''),
            'categoria': categoria.get('name', 'Sin categoría'),
        }

        productos_completos.append(producto_completo)
        
        

    productos = productos_completos

    return render(request, 'productos/productos.html', {
        'productos': productos,
        'busqueda': busqueda,
    })"""
    
def get_user_info(request):
    id_token = request.session.get('id_token')
    if not id_token:
        return None
    try:
        payload = jwt.decode(id_token, options={"verify_signature": False})
        return payload  # Para obtener nombre de usuario, mail.
    except jwt.DecodeError:
        return None
    
def logout(request):
    if not check_login(request):
        return redirect('/login')
    
    # Limpiar la sesión
    request.session.flush()
    
    return redirect('/login')


def login(request):
    
    if check_login(request):
        return redirect('/index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        response = requests.post('http://35.168.133.16:3000/login', json={
            'username': username,
            'password': password
        })

        if response.status_code == 200:
            print("Login exitoso, guardando token en sesión")
            data = response.json()
            request.session['id_token'] = data.get('token')   
            request.session['access_token'] = data.get('accessToken') 
            request.session['refresh_token'] = data.get('refreshToken')
            return redirect('/index')  
        elif response.status_code == 400:
            return render(request, 'login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })
        elif response.status_code == 401:
            return render(request, 'login.html', {
                'error': 'El acceso no fue autorizado.'
            })
        else:
            return render(request, 'login.html', {
                'error': f'{response.status_code}: Servicio no disponible en este momento. Inténtalo de nuevo más tarde.'
            })

    return render(request, 'login.html')

def eliminar_categoria(request, id):
    
    if not check_login(request):
        return redirect('/login')
    
    categoria = get_object_or_404(Categoria, id=id)
    categoria.delete()
    return redirect('listar_categorias')  # Redirige a donde listas las categorías
    

def listar_categorias(request):
    
    if not check_login(request):
        return redirect('/login')
    
    # Obtener el término de búsqueda (si existe)
    busqueda = request.GET.get('q', '')
    
    # Filtrar categorías si hay búsqueda
    if busqueda:
        categorias_list = Categoria.objects.filter(nombre__icontains=busqueda).order_by('nombre')
    else:
        categorias_list = Categoria.objects.all().order_by('nombre')
    
    # Paginación (10 items por página)
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
        'busqueda': busqueda  # Para mantener el valor en el input
    })
    
def nueva_categoria(request):
    
    if not check_login(request):
        return redirect('/login')
    
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
            
    context = {
        'form': form,
    }
    
    return render(request, 'categorias/nueva.html', context)


def modificar_categoria(request, id):
    
    if not check_login(request):
        return redirect('/login')
    
    categoria = get_object_or_404(Categoria, id=id)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('listar_categorias')  # Redirige a la lista después de editar
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'categorias/modificar.html', {
        'form': form,
        'categoria': categoria
    })
    
    
def error_404_view(request, exception):
    return render(request, '404.html', status=404)