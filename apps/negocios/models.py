# apps/negocios/models.py
from django.db import models
from django.contrib.auth.models import User
from apps.usuarios.models import Perfil
from django.utils import timezone
from datetime import timedelta
import django.db.models as models  # Para Avg


class CategoriaNegocio(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    icono = models.CharField(max_length=50, blank=True, help_text="Ej: scissors, car, coffee")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías de Negocio"
        ordering = ['nombre']


class Negocio(models.Model):
    propietario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='negocios'
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.ForeignKey(
        CategoriaNegocio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='negocios'
    )
    ciudad = models.CharField(max_length=50)
    direccion = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=15, blank=True)  # opcional
    horario = models.CharField(max_length=100, blank=True)
    instagram = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)

    # NUEVAS 6 FOTOS
    imagen_principal = models.ImageField(upload_to='negocios/', blank=True, null=True)
    imagen_1 = models.ImageField(upload_to='negocios/', blank=True, null=True)
    imagen_2 = models.ImageField(upload_to='negocios/', blank=True, null=True)
    imagen_3 = models.ImageField(upload_to='negocios/', blank=True, null=True)
    imagen_4 = models.ImageField(upload_to='negocios/', blank=True, null=True)
    imagen_5 = models.ImageField(upload_to='negocios/', blank=True, null=True)

    # FOTO ANTIGUA (compatibilidad con datos existentes)
    imagen = models.ImageField(upload_to='negocios/', null=True, blank=True)

    destacado = models.BooleanField(default=False)
    fecha_destacado = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    def es_destacado_activo(self):
        if self.destacado and self.fecha_destacado:
            return timezone.now() <= self.fecha_destacado + timedelta(days=7)
        return False

    # PROMEDIO DE CALIFICACIÓN
    def promedio_calificacion(self):
        califs = self.propietario.perfil.calificaciones_recibidas_global.all()
        if califs.exists():
            avg = califs.aggregate(avg=models.Avg('puntuacion'))['avg']
            return round(avg or 0, 1)
        return 0

    def total_calificaciones(self):
        return self.propietario.perfil.calificaciones_recibidas_global.count()

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name_plural = "Negocios"


class Favorito(models.Model):
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='favoritos_negocios'
    )
    negocio = models.ForeignKey(
        Negocio, 
        on_delete=models.CASCADE, 
        related_name='favoritos'
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'negocio')
        verbose_name = 'Favorito de Negocio'
        verbose_name_plural = 'Favoritos de Negocios'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario.username} → {self.negocio.nombre}"