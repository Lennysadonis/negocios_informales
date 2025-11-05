from django.apps import AppConfig

class ProductosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.productos'
    label = 'productos'
    # ELIMINA EL ready() → NO SE USA MÁS