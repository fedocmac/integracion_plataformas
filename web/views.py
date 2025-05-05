from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CategoriaForm
from .models import Categoria, Producto, Compra
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied

# Create your views here.
def index(request):
    return HttpResponse("Hola desde la vista index de la app web.")

def confirmar_compra(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)
    producto = compra.producto  # El producto relacionado con la compra

    return render(request, 'productos/confirmar_compra.html', {
        'producto': producto,
        'compra': compra
    })

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    
    if request.method == 'POST':
        # Procesar compra directamente
        compra = Compra.objects.create(producto=producto)
        return redirect('confirmar_compra', compra_id=compra.id)  # Redirige a la URL correcta con el ID de la compra
    
    return render(request, 'productos/detalle_producto.html', {
        'producto': producto
    })
    
    
def historial_compras(request):
    
    compras_list = Compra.objects.all()
    
    paginator = Paginator(compras_list, 10)
    page = request.GET.get('page')
    
    try:
        compras  = paginator.page(page)
    except PageNotAnInteger:
        compras = paginator.page(1)
    except EmptyPage:
        compras = paginator.page(paginator.num_pages)
    
    return render(request, 'productos/historial_compras.html', {
        'compras': compras
    })
    

def listar_productos(request):
    # Obtener el término de búsqueda (si existe)
    busqueda = request.GET.get('q', '')
    
    # Filtrar categorías si hay búsqueda
    if busqueda:
        productos_list = Producto.objects.filter(nombre__icontains=busqueda).order_by('nombre')
    else:
        productos_list = Producto.objects.all().order_by('nombre')
    
    # Paginación (10 items por página)
    paginator = Paginator(productos_list, 10)
    page = request.GET.get('page')
    
    try:
        productos  = paginator.page(page)
    except PageNotAnInteger:
        productos = paginator.page(1)
    except EmptyPage:
        productos = paginator.page(paginator.num_pages)
    
    return render(request, 'productos/productos.html', {
        'productos': productos,
        'busqueda': busqueda  # Para mantener el valor en el input
    })

def productos(request):
    return render(request, 'productos/productos.html')

def login(request):
    return render(request, 'login.html')  # Redirige a donde listas las categorías

def eliminar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    categoria.delete()
    return redirect('listar_categorias')  # Redirige a donde listas las categorías
    

def listar_categorias(request):
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