from django.contrib import admin
from .models import Negocio, CategoriaNegocio

@admin.register(CategoriaNegocio)
class CategoriaNegocioAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']

@admin.register(Negocio)
class NegocioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'propietario', 'ciudad', 'categoria', 'aprobado']
    list_filter = ['aprobado', 'ciudad', 'categoria']
    search_fields = ['nombre', 'propietario__username']