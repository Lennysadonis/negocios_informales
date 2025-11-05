# apps/favoritos/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# IMPORTS CORRECTOS (ajusta según tus nombres reales)
from apps.negocios.models import Favorito as FavoritoNegocio
from apps.productos.models import FavoritoProducto  # ← Este es el nombre correcto
from apps.servicios.models import FavoritoServicio


@login_required
def mis_favoritos(request):
    # NEGOCIOS
    favoritos_negocios = FavoritoNegocio.objects.filter(usuario=request.user).select_related(
        'negocio', 'negocio__categoria', 'negocio__propietario'
    )
    # PRODUCTOS
    favoritos_productos = FavoritoProducto.objects.filter(usuario=request.user).select_related(
        'producto', 'producto__categoria', 'producto__propietario'
    )
    # SERVICIOS
    favoritos_servicios = FavoritoServicio.objects.filter(usuario=request.user).select_related(
        'servicio', 'servicio__categoria', 'servicio__propietario'
    )

    context = {
        'favoritos_negocios': favoritos_negocios,
        'favoritos_productos': favoritos_productos,
        'favoritos_servicios': favoritos_servicios,
    }
    return render(request, 'favoritos.html', context)