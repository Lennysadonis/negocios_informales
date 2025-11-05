from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'  # ¡IMPORTANTE! Debe ser el path completo
    label = 'usuarios'      # Opcional, pero recomendado