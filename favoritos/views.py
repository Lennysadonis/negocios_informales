# apps/favoritos/views.py
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def favorito_negocio(request, negocio_id):
    # Aquí iría la lógica real (modelo FavoritoNegocio, etc.)
    messages.success(request, "Negocio añadido a favoritos")
    return redirect('home:index')

@login_required
def favorito_producto(request, producto_id):
    messages.success(request, "Producto añadido a favoritos")
    return redirect('home:index')

@login_required
def favorito_servicio(request, servicio_id):
    messages.success(request, "Servicio añadido a favoritos")
    return redirect('home:index')