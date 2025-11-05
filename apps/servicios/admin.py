# apps/servicios/admin.py
from django.contrib import admin
from .models import Servicio, CategoriaServicio

@admin.register(CategoriaServicio)
class CategoriaServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'propietario', 'precio', 'ciudad', 'disponible', 'aprobado']
    list_filter = ['ciudad', 'categoria', 'disponible', 'aprobado']
    search_fields = ['nombre', 'descripcion', 'propietario__username']
    readonly_fields = ['promedio_calificacion']
    list_editable = ['aprobado', 'disponible']