from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db.models.functions import Lower


class Categoria(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        
        error_messages={
        'unique': 'Ya existe una categoría con este nombre. Por favor, elige otro.',
        'required': 'Este campo es obligatorio.',
    }
    )
    description = models.CharField(
        max_length=250,
        verbose_name='Descripción',
        blank=True,  # Opcional
        null=True   # Opcional
    )

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']  # Orden alfabético por defecto
        
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                name='unique_categoria_name_ci'
            )
        ]

    def __str__(self):
        return self.name  # Representación legible en el admin/consola
    

"""class Producto(models.Model):
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        unique=True
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio',
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,  # Si se borra la categoría, el campo se pondrá a NULL
        verbose_name='Categoría',
        blank=True,
        null=True,
        related_name='productos'  # Permite acceder a los productos desde una categoría: categoria.productos.all()
    )

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
"""
    
class Compra(models.Model):
    producto_id = models.IntegerField(verbose_name='ID del producto')
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de compra'
    )
    precio_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio al momento de compra'
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-fecha']  # Más recientes primero
        indexes = [
            models.Index(fields=['-fecha']),  # Índice para búsquedas por fecha
        ]