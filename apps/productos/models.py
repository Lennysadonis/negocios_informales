# apps/productos/models.py
from django.db import models
from django.contrib.auth.models import User
from apps.usuarios.models import Perfil
from apps.negocios.models import Negocio
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg


class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías de Producto"


class Producto(models.Model):
    # TIPOS DE PRECIO
    TIPOS_PRECIO = [
        ('unidad', 'Por Unidad'),
        ('paquete', 'Por Paquete'),
        ('docena', 'Por Docena'),
        ('otro', 'Otro'),
    ]

    # MONEDAS
    MONEDAS = [
        ('C$', 'Córdoba (C$)'),
        ('USD', 'Dólar (USD)'),
        ('EUR', 'Euro (€)'),
    ]

    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productos')
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, null=True, blank=True, related_name='productos')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_precio = models.CharField(max_length=10, choices=TIPOS_PRECIO, default='unidad')
    moneda = models.CharField(max_length=5, choices=MONEDAS, default='C$')  # NUEVO
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.SET_NULL, null=True, blank=True)
    stock = models.PositiveIntegerField(default=1)

    # IMAGEN PRINCIPAL + 5 FOTOS
    imagen_principal = models.ImageField(upload_to='productos/', null=True, blank=True)
    imagen_1 = models.ImageField(upload_to='productos/', null=True, blank=True)
    imagen_2 = models.ImageField(upload_to='productos/', null=True, blank=True)
    imagen_3 = models.ImageField(upload_to='productos/', null=True, blank=True)
    imagen_4 = models.ImageField(upload_to='productos/', null=True, blank=True)
    imagen_5 = models.ImageField(upload_to='productos/', null=True, blank=True)

    # CONTROL
    destacado = models.BooleanField(default=False)
    fecha_destacado = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.precio} {self.moneda} / {self.get_tipo_precio_display()}"

    def es_destacado_activo(self):
        if self.destacado and self.fecha_destacado:
            return timezone.now() <= self.fecha_destacado + timedelta(days=7)
        return False

    # PROMEDIO DE CALIFICACIÓN DEL PERFIL
    def promedio_calificacion(self):
        califs = self.propietario.perfil.calificaciones_recibidas_global.all()
        if califs.exists():
            avg = califs.aggregate(avg=Avg('puntuacion'))['avg']
            return round(avg or 0, 1)
        return 0

    def total_calificaciones(self):
        return self.propietario.perfil.calificaciones_recibidas_global.count()

    class Meta:
        ordering = ['-fecha_creacion']


# FAVORITO PARA PRODUCTOS
class FavoritoProducto(models.Model):
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='favoritos_productos'
    )
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE, 
        related_name='favoritos'
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'producto')
        verbose_name = 'Favorito de Producto'
        verbose_name_plural = 'Favoritos de Productos'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario.username} → {self.producto.nombre}"