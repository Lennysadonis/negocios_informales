from django.apps import AppConfig


class ServiciosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.servicios'  # ← DEBE SER EL NOMBRE COMPLETO
    verbose_name = 'Servicios'