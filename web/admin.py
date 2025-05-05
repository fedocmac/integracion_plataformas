from django.contrib import admin
from .models import Categoria, Producto  # Importa tu modelo

admin.site.register(Categoria)  # Registra el modelo para que sea visible
admin.site.register(Producto)  # Registra el modelo para que sea visible