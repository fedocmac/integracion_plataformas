from django.contrib import admin
from .models import Compra, Categoria

admin.site.register(Categoria)  # Registra el modelo para que sea visible
admin.site.register(Compra)