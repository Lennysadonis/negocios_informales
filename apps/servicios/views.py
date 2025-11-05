# apps/servicios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Case, When
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
import django.db.models as models

from .models import Servicio, FavoritoServicio, CategoriaServicio
from .forms import ServicioForm
from apps.usuarios.models import Calificacion
from apps.usuarios.forms import CalificacionForm


def lista_servicios(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    ciudad = request.GET.get('ciudad', '')

    servicios = Servicio.objects.filter(aprobado=True).select_related('propietario', 'categoria')

    if query:
        servicios = servicios.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(ciudad__icontains=query)
        )
    if categoria_id:
        servicios = servicios.filter(categoria_id=categoria_id)
    if ciudad:
        servicios = servicios.filter(ciudad__icontains=ciudad)

    # DESTACADOS PRIMERO (7 días)
    ahora = timezone.now()
    servicios = servicios.annotate(
        orden_destacado=Case(
            When(destacado=True, fecha_destacado__gte=ahora - timezone.timedelta(days=7), then=0),
            default=1,
            output_field=models.IntegerField()
        )
    ).order_by('orden_destacado', '-fecha_creacion')

    paginator = Paginator(servicios, 12)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)

    # AGREGAR total_fotos A CADA SERVICIO
    for s in page_obj:
        fotos = [
            s.imagen_principal,
            s.imagen_1, s.imagen_2, s.imagen_3, s.imagen_4, s.imagen_5,
            s.imagen if not any([s.imagen_principal, s.imagen_1, s.imagen_2, s.imagen_3, s.imagen_4, s.imagen_5]) else None
        ]
        s.total_fotos = sum(1 for f in fotos if f)

    context = {
        'page_obj': page_obj,
        'object_list': page_obj,
        'query': query,
        'categoria_id': categoria_id,
        'ciudad': ciudad,
        'categorias': CategoriaServicio.objects.all(),
        'ciudades': Servicio.objects.values_list('ciudad', flat=True).distinct().order_by('ciudad'),
    }

    # AJAX para paginación infinita
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('servicios/_lista.html', context, request=request)
        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next(),
            'page_number': page_obj.number,
            'num_pages': page_obj.paginator.num_pages
        })

    return render(request, 'servicios/lista.html', context)


@login_required
def publicar_servicio(request):
    # VALIDAR WHATSAPP
    if not request.user.perfil.whatsapp:
        messages.error(
            request,
            "¡Necesitas agregar tu WhatsApp en tu perfil para publicar servicios! "
            "<a href='/perfil/' class='text-decoration-underline fw-bold'>Ir al perfil</a>"
        )
        return redirect('usuarios:perfil')

    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            servicio = form.save(commit=False)
            servicio.propietario = request.user
            servicio.save()
            messages.success(request, '¡Servicio publicado! Ya te pueden contratar por WhatsApp')
            return redirect('servicios:detalle', pk=servicio.pk)
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = ServicioForm(user=request.user)

    return render(request, 'servicios/publicar.html', {'form': form})


@login_required
def borrar_servicio(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk, propietario=request.user)
    if request.method == 'POST':
        servicio.delete()
        messages.success(request, 'Servicio eliminado.')
    return redirect('usuarios:perfil')


def detalle_servicio(request, pk):
    servicio = get_object_or_404(
        Servicio.objects.select_related('propietario__perfil', 'categoria'),
        pk=pk, aprobado=True
    )

    # CONTAR FOTOS
    fotos = [
        servicio.imagen_principal,
        servicio.imagen_1, servicio.imagen_2, servicio.imagen_3, servicio.imagen_4, servicio.imagen_5,
        servicio.imagen if not any([servicio.imagen_principal, servicio.imagen_1, servicio.imagen_2, servicio.imagen_3, servicio.imagen_4, servicio.imagen_5]) else None
    ]
    total_fotos = sum(1 for f in fotos if f)

    es_favorito = False
    ya_calificado = False
    form_calificacion = CalificacionForm()

    if request.user.is_authenticated:
        es_favorito = FavoritoServicio.objects.filter(usuario=request.user, servicio=servicio).exists()
        ya_calificado = Calificacion.objects.filter(
            usuario=request.user,
            perfil_calificado=servicio.propietario.perfil
        ).exists()

        if request.method == 'POST' and not ya_calificado and request.user != servicio.propietario:
            form_calificacion = CalificacionForm(request.POST)
            if form_calificacion.is_valid():
                Calificacion.objects.update_or_create(
                    usuario=request.user,
                    perfil_calificado=servicio.propietario.perfil,
                    defaults={
                        'puntuacion': form_calificacion.cleaned_data['puntuacion'],
                        'comentario': form_calificacion.cleaned_data['comentario']
                    }
                )
                messages.success(request, '¡Gracias por tu calificación!')
                return redirect('servicios:detalle', pk=pk)
        else:
            form_calificacion = CalificacionForm()

    calificaciones = servicio.propietario.perfil.calificaciones_recibidas_global.select_related('usuario').order_by('-fecha')

    return render(request, 'servicios/detalle.html', {
        'servicio': servicio,
        'es_favorito': es_favorito,
        'ya_calificado': ya_calificado,
        'calificaciones': calificaciones,
        'form_calificacion': form_calificacion,
        'total_fotos': total_fotos  # NUEVO
    })


@login_required
def toggle_favorito_servicio(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    favorito, created = FavoritoServicio.objects.get_or_create(usuario=request.user, servicio=servicio)
    if not created:
        favorito.delete()
        action = 'removed'
    else:
        action = 'added'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'action': action})

    messages.success(request, 'Favorito actualizado')
    return redirect('servicios:detalle', pk=pk)