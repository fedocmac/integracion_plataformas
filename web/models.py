from django.db import models
from django.core.validators import MinLengthValidator


class Categoria(models.Model):
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        unique=True  # Evita nombres duplicados
    )
    descripcion = models.CharField(
        max_length=250,
        verbose_name='Descripción',
        blank=True,  # Opcional
        null=True   # Opcional
    )

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']  # Orden alfabético por defecto

    def __str__(self):
        return self.nombre  # Representación legible en el admin/consola