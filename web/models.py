from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator


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
    

class Producto(models.Model):
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        unique=True  # Evita nombres duplicados
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio',
        blank=True,  # Opcional
        null=True,   # Opcional
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']  # Orden alfabético por defecto

    def __str__(self):
        return self.nombre  # Representación legible en el admin/consola