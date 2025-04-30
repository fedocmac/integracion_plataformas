from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CategoriaForm
from .models import Categoria
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied

# Create your views here.
def index(request):
    return HttpResponse("Hola desde la vista index de la app web.")

def compras(request):
    return render(request, 'compras/compras.html')

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