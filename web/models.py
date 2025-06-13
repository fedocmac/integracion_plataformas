from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator



class UsuarioRegistro(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)
    confirmado = models.BooleanField(default=False)
    codigo_confirmacion = models.CharField(max_length=10, blank=True, null=True)   # <-- AGREGA ESTA LINEA

    def __str__(self):
        return self.username

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
        return self.nombre  # Representación legible en el admin/consola
    
    
class Compra(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,  # Evita borrar productos con compras registradas
        verbose_name='Producto comprado'
    )
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

    def __str__(self):
        return f"Compra #{self.id} - {self.producto.nombre}"

    def save(self, *args, **kwargs):
        """Guarda el precio actual del producto al momento de la compra"""
        if not self.precio_compra:  # Solo si no se especificó un precio
            self.precio_compra = self.producto.precio
        super().save(*args, **kwargs)