# apps/usuarios/models.py
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True, default='perfiles/default.png')
    bio = models.TextField(max_length=500, blank=True)
    telefono = models.CharField(max_length=15, blank=True)
    whatsapp = models.CharField(
        max_length=16,  # AUMENTADO PARA +505 + 8 dígitos
        blank=True,
        null=True,
        help_text="Ej: +50557277494, +15551234567"
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def get_foto_url(self):
        if self.foto and hasattr(self.foto, 'url'):
            return self.foto.url
        return '/static/img/default-user.png'


# === CREA PERFIL AL REGISTRAR USUARIO ===
@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)


# === GUARDA PERFIL AL ACTUALIZAR USUARIO ===
@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()


# === CALIFICACIÓN UNIFICADA ===
class Calificacion(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='calificaciones_dadas_global'
    )
    perfil_calificado = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='calificaciones_recibidas_global'
    )
    puntuacion = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} estrella{'s' if i > 1 else ''}") for i in range(1, 6)]
    )
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'perfil_calificado')
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario} - {self.puntuacion} - {self.perfil_calificado.user.username}"