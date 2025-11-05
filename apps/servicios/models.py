# apps/servicios/models.py
from django.db import models
from django.contrib.auth.models import User
from apps.usuarios.models import Perfil
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg


class CategoriaServicio(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    icono = models.CharField(max_length=50, blank=True, help_text="Ej: tools, paint-brush, car-repair")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías de Servicio"
        ordering = ['nombre']


class Servicio(models.Model):
    TIPOS_PRECIO = [
        ('hora', 'Por Hora'),
        ('dia', 'Por Día'),
        ('proyecto', 'Por Proyecto'),
        ('fijo', 'Precio Fijo'),
    ]

    MONEDAS = [
        ('C$', 'Córdoba (C$)'),
        ('USD', 'Dólar (USD)'),
        ('EUR', 'Euro (€)'),
    ]

    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='servicios')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.ForeignKey(CategoriaServicio, on_delete=models.SET_NULL, null=True, blank=True)
    ciudad = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_precio = models.CharField(max_length=10, choices=TIPOS_PRECIO, default='hora')
    moneda = models.CharField(max_length=5, choices=MONEDAS, default='C$')
    experiencia = models.CharField(max_length=100, blank=True, help_text="Ej: 5 años, Certificado")
    disponible = models.BooleanField(default=True)

    # 6 FOTOS
    imagen_principal = models.ImageField(upload_to='servicios/', blank=True, null=True)
    imagen_1 = models.ImageField(upload_to='servicios/', blank=True, null=True)
    imagen_2 = models.ImageField(upload_to='servicios/', blank=True, null=True)
    imagen_3 = models.ImageField(upload_to='servicios/', blank=True, null=True)
    imagen_4 = models.ImageField(upload_to='servicios/', blank=True, null=True)
    imagen_5 = models.ImageField(upload_to='servicios/', blank=True, null=True)

    # FOTO ANTIGUA (compatibilidad)
    imagen = models.ImageField(upload_to='servicios/', null=True, blank=True)

    # Destacado
    destacado = models.BooleanField(default=False)
    fecha_destacado = models.DateTimeField(null=True, blank=True)

    # Control
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
        verbose_name_plural = "Servicios"


# FAVORITO PARA SERVICIOS
class FavoritoServicio(models.Model):
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='favoritos_servicios'
    )
    servicio = models.ForeignKey(
        Servicio, 
        on_delete=models.CASCADE, 
        related_name='favoritos'
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'servicio')
        verbose_name = 'Favorito de Servicio'
        verbose_name_plural = 'Favoritos de Servicios'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario.username} → {self.servicio.nombre}"