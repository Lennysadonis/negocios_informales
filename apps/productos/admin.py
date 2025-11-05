from django.contrib import admin
from .models import CategoriaProducto, Producto

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'propietario', 'aprobado']
    list_filter = ['aprobado', 'categoria', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']