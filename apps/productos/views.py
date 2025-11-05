# apps/productos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Case, When, IntegerField
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Producto, CategoriaProducto, FavoritoProducto
from .forms import ProductoForm
from apps.usuarios.models import Calificacion
from apps.usuarios.forms import CalificacionForm


def lista_productos(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    precio_max = request.GET.get('precio_max', '')

    productos = Producto.objects.filter(aprobado=True).select_related('propietario', 'categoria', 'negocio')

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query)
        )
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if precio_max:
        try:
            productos = productos.filter(precio__lte=float(precio_max))
        except:
            pass

    productos = productos.annotate(
        orden_destacado=Case(
            When(destacado=True, fecha_destacado__gte=timezone.now() - timezone.timedelta(days=7), then=0),
            default=1,
            output_field=IntegerField()
        )
    ).order_by('orden_destacado', '-fecha_creacion')

    paginator = Paginator(productos, 12)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)

    # AJAX PARA PAGINACIÓN
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('productos/_lista.html', {'object_list': page_obj}, request=request)
        return JsonResponse({'html': html, 'has_next': page_obj.has_next()})

    return render(request, 'productos/lista.html', {
        'object_list': page_obj,        # CLAVE PARA _lista.html
        'query': query,
        'categoria_id': categoria_id,
        'precio_max': precio_max,
        'categorias': CategoriaProducto.objects.all()
    })


@login_required
def publicar_producto(request):
    # VALIDAR WHATSAPP EN PERFIL
    if not request.user.perfil.whatsapp:
        messages.error(
            request,
            "¡Necesitas agregar tu WhatsApp en tu perfil para publicar productos! "
            "<a href='/usuarios/perfil/' class='text-decoration-underline fw-bold'>Ir al perfil</a>",
            extra_tags='safe'
        )
        return redirect('usuarios:perfil')

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.propietario = request.user
            producto.save()

            messages.success(request, '¡Producto publicado! Listo para vender por WhatsApp')
            return redirect('productos:detalle', pk=producto.pk)
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = ProductoForm(user=request.user)

    return render(request, 'productos/publicar.html', {'form': form})


def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk, aprobado=True)
    es_favorito = False
    ya_calificado = False
    form_calificacion = CalificacionForm()

    if request.user.is_authenticated:
        es_favorito = FavoritoProducto.objects.filter(usuario=request.user, producto=producto).exists()
        ya_calificado = Calificacion.objects.filter(
            usuario=request.user,
            perfil_calificado=producto.propietario.perfil
        ).exists()

        # PROCESAR CALIFICACIÓN
        if request.method == 'POST' and not ya_calificado and request.user != producto.propietario:
            form_calificacion = CalificacionForm(request.POST)
            if form_calificacion.is_valid():
                Calificacion.objects.update_or_create(
                    usuario=request.user,
                    perfil_calificado=producto.propietario.perfil,
                    defaults={
                        'puntuacion': form_calificacion.cleaned_data['puntuacion'],
                        'comentario': form_calificacion.cleaned_data['comentario']
                    }
                )
                messages.success(request, '¡Gracias por tu calificación!')
                return redirect('productos:detalle', pk=pk)
        else:
            form_calificacion = CalificacionForm()

    context = {
        'producto': producto,
        'es_favorito': es_favorito,
        'ya_calificado': ya_calificado,
        'form_calificacion': form_calificacion,
    }
    return render(request, 'productos/detalle.html', context)


@login_required
def favorito_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    favorito, created = FavoritoProducto.objects.get_or_create(usuario=request.user, producto=producto)
    if not created:
        favorito.delete()
        messages.success(request, 'Quitado de favoritos')
    else:
        messages.success(request, '¡Agregado a favoritos!')
    return redirect('productos:detalle', pk=pk)


@login_required
def borrar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk, propietario=request.user)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado.')
    return redirect('usuarios:perfil')