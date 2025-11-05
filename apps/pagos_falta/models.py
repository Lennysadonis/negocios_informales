from django.db import models
from django.contrib.auth.models import User
from apps.negocios.models import Negocio
from django.utils import timezone
from datetime import timedelta

# PLANES DE PROMOCIÓN
PLANES_PROMOCION = [
    ('24h', '24 horas - $1.00'),
    ('3d', '3 días - $2.50'),
    ('7d', '7 días - $5.00'),
]

class Promocion(models.Model):
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE)
    plan = models.CharField(max_length=3, choices=PLANES_PROMOCION)
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if self.pagado and not self.fecha_pago:
            self.fecha_pago = timezone.now()
            if self.plan == '24h':
                self.fecha_expiracion = self.fecha_pago + timedelta(hours=24)
            elif self.plan == '3d':
                self.fecha_expiracion = self.fecha_pago + timedelta(days=3)
            elif self.plan == '7d':
                self.fecha_expiracion = self.fecha_pago + timedelta(days=7)
        super().save(*args, **kwargs)

    def esta_activa(self):
        return self.pagado and timezone.now() < self.fecha_expiracion

    def __str__(self):
        return f"{self.negocio.nombre} - {self.get_plan_display()}"
    
    
class Anuncio(models.Model):
    titulo = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to='anuncios/')
    enlace = models.URLField(blank=True)
    pagado = models.BooleanField(default=False)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)

    def esta_activo(self):
        return self.pagado and timezone.now() >= self.fecha_inicio and timezone.now() <= self.fecha_fin

    def __str__(self):
        return self.titulo