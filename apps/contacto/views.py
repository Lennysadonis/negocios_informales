# apps/contacto/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def mensajes(request):
    # SIN MODELOS → Usamos favoritos para mostrar conversaciones
    from apps.negocios.models import Favorito as FavoritoNegocio
    from apps.productos.models import FavoritoProducto
    from apps.servicios.models import FavoritoServicio

    usuarios = set()

    for f in FavoritoNegocio.objects.filter(usuario=request.user):
        if f.negocio.propietario != request.user:
            usuarios.add(f.negocio.propietario)
    for f in FavoritoProducto.objects.filter(usuario=request.user):
        if f.producto.propietario != request.user:
            usuarios.add(f.producto.propietario)
    for f in FavoritoServicio.objects.filter(usuario=request.user):
        if f.servicio.propietario != request.user:
            usuarios.add(f.servicio.propietario)

    conversaciones = [
        {
            'other_user': u,
            'last_message': '¡Hola! ¿Te interesa mi anuncio?'
        }
        for u in usuarios
    ]

    return render(request, 'contacto/mensajes.html', {
        'conversaciones': conversaciones
    })

@login_required
def chat_room(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        return render(request, 'contacto/error.html', {'msg': 'No puedes chatear contigo mismo'})

    room_name = f"chat_{min(request.user.id, user_id)}_{max(request.user.id, user_id)}"

    return render(request, 'contacto/room.html', {
        'other_user': other_user,
        'room_name': room_name
    })