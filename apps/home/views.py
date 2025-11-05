# apps/home/views.py
from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from apps.negocios.models import Negocio, CategoriaNegocio
from apps.productos.models import Producto, CategoriaProducto
from apps.servicios.models import Servicio, CategoriaServicio


def index(request):
    hoy = timezone.now()
    siete_dias_atras = hoy - timedelta(days=7)
    
    destacados_negocios = Negocio.objects.filter(
        destacado=True,
        fecha_destacado__gte=siete_dias_atras,
        aprobado=True
    ).select_related('categoria', 'propietario__perfil')[:6]
    
    destacados_productos = Producto.objects.filter(
        destacado=True,
        fecha_destacado__gte=siete_dias_atras,
        aprobado=True
    ).select_related('categoria', 'negocio', 'propietario__perfil')[:6]

    destacados_servicios = Servicio.objects.filter(
        destacado=True,
        fecha_destacado__gte=siete_dias_atras,
        aprobado=True,
        disponible=True
    ).select_related('categoria', 'propietario__perfil')[:6]

    return render(request, 'home/index.html', {
        'destacados_negocios': destacados_negocios,
        'destacados_productos': destacados_productos,
        'destacados_servicios': destacados_servicios,
    })


def explora(request):
    # === MODELOS CON OPTIMIZACIÓN ===
    negocios = Negocio.objects.filter(aprobado=True).select_related(
        'categoria', 'propietario__perfil'
    )
    productos = Producto.objects.filter(aprobado=True).select_related(
        'categoria', 'negocio', 'propietario__perfil'
    )
    servicios = Servicio.objects.filter(aprobado=True, disponible=True).select_related(
        'categoria', 'propietario__perfil'
    )

    # === FILTROS ===
    query = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')
    tipo = request.GET.get('tipo', '')

    if query:
        negocios = negocios.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(ciudad__icontains=query)
        )
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query)
        )
        servicios = servicios.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(ciudad__icontains=query)
        )

    if categoria:
        negocios = negocios.filter(categoria__nombre__icontains=categoria)
        productos = productos.filter(categoria__nombre__icontains=categoria)
        servicios = servicios.filter(categoria__nombre__icontains=categoria)

    # === FILTRO POR TIPO (MANTIENE SOLO UNO SI SE SELECCIONA) ===
    if tipo == 'negocio':
        productos = Producto.objects.none()
        servicios = Servicio.objects.none()
    elif tipo == 'producto':
        negocios = Negocio.objects.none()
        servicios = Servicio.objects.none()
    elif tipo == 'servicio':
        negocios = Negocio.objects.none()
        productos = Producto.objects.none()

    # === LIMITAR RESULTADOS ===
    negocios = negocios[:10]
    productos = productos[:10]
    servicios = servicios[:10]

    # === AGREGAR total_fotos A NEGOCIOS ===
    for n in negocios:
        fotos = [
            n.imagen_principal,
            n.imagen_1, n.imagen_2, n.imagen_3, n.imagen_4, n.imagen_5,
            n.imagen if not any([n.imagen_principal, n.imagen_1, n.imagen_2, n.imagen_3, n.imagen_4, n.imagen_5]) else None
        ]
        n.total_fotos = sum(1 for f in fotos if f)

    # === AGREGAR total_fotos A SERVICIOS (PARA CARRUSEL) ===
    for s in servicios:
        fotos = [
            s.imagen_principal,
            s.imagen_1, s.imagen_2, s.imagen_3, s.imagen_4, s.imagen_5,
            s.imagen if not any([s.imagen_principal, s.imagen_1, s.imagen_2, s.imagen_3, s.imagen_4, s.imagen_5]) else None
        ]
        s.total_fotos = sum(1 for f in fotos if f)

    # === CATEGORÍAS UNIFICADAS ===
    categorias_negocios = CategoriaNegocio.objects.values_list('nombre', flat=True)
    categorias_productos = CategoriaProducto.objects.values_list('nombre', flat=True)
    categorias_servicios = CategoriaServicio.objects.values_list('nombre', flat=True)
    
    categorias = sorted(list(set(
        list(categorias_negocios) +
        list(categorias_productos) +
        list(categorias_servicios)
    )))

    # === CONTEXTO ===
    return render(request, 'home/explora.html', {
        'negocios': negocios,
        'object_list_productos': productos,
        'object_list_servicios': servicios,  # SERVICIOS APARECEN
        'categorias': categorias,
        'query': query,
        'categoria_seleccionada': categoria,
        'tipo': tipo,
    })