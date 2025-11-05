# apps/negocios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Case, When
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
import django.db.models as models

from .models import Negocio, Favorito, CategoriaNegocio
from .forms import NegocioForm
from apps.usuarios.models import Calificacion
from apps.usuarios.forms import CalificacionForm


def lista_negocios(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    ciudad = request.GET.get('ciudad', '')

    negocios = Negocio.objects.filter(aprobado=True).select_related('propietario', 'categoria')

    if query:
        negocios = negocios.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(ciudad__icontains=query)
        )
    if categoria_id:
        negocios = negocios.filter(categoria_id=categoria_id)
    if ciudad:
        negocios = negocios.filter(ciudad__icontains=ciudad)

    ahora = timezone.now()
    negocios = negocios.annotate(
        orden_destacado=Case(
            When(destacado=True, fecha_destacado__gte=ahora - timezone.timedelta(days=7), then=0),
            default=1,
            output_field=models.IntegerField()
        )
    ).order_by('orden_destacado', '-fecha_creacion')

    paginator = Paginator(negocios, 12)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)

    # AGREGAR total_fotos A CADA NEGOCIO EN LISTA
    for n in page_obj:
        fotos = [
            n.imagen_principal,
            n.imagen_1, n.imagen_2, n.imagen_3, n.imagen_4, n.imagen_5,
            n.imagen if not any([n.imagen_principal, n.imagen_1, n.imagen_2, n.imagen_3, n.imagen_4, n.imagen_5]) else None
        ]
        n.total_fotos = sum(1 for f in fotos if f)

    context = {
        'page_obj': page_obj,
        'object_list': page_obj,
        'query': query,
        'categoria_id': categoria_id,
        'ciudad': ciudad,
        'categorias': CategoriaNegocio.objects.all(),
        'ciudades': Negocio.objects.values_list('ciudad', flat=True).distinct().order_by('ciudad'),
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('negocios/_lista.html', context, request=request)
        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next(),
            'page_number': page_obj.number,
            'num_pages': page_obj.paginator.num_pages
        })

    return render(request, 'negocios/lista.html', context)


@login_required
def publicar_negocio(request):
    # VALIDAR QUE EL USUARIO TENGA WHATSAPP EN SU PERFIL
    if not request.user.perfil.whatsapp:
        messages.error(
            request,
            "¡Necesitas agregar tu WhatsApp en tu perfil para publicar un negocio! "
            "<a href='/perfil/' class='text-decoration-underline fw-bold'>Ir al perfil</a>"
        )
        return redirect('usuarios:perfil')

    if request.method == 'POST':
        form = NegocioForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            negocio = form.save(commit=False)
            negocio.propietario = request.user
            negocio.usuario = request.user  # compatibilidad
            negocio.save()

            messages.success(request, '¡Negocio publicado! Tus clientes ya te pueden chatear por WhatsApp')
            return redirect('negocios:detalle', pk=negocio.pk)
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = NegocioForm(user=request.user)

    return render(request, 'negocios/publicar.html', {'form': form})


@login_required
def borrar_negocio(request, pk):
    negocio = get_object_or_404(Negocio, pk=pk, propietario=request.user)
    if request.method == 'POST':
        negocio.delete()
        messages.success(request, 'Negocio eliminado.')
    return redirect('usuarios:perfil')


def detalle_negocio(request, pk):
    negocio = get_object_or_404(
        Negocio.objects.select_related('propietario__perfil', 'categoria'),
        pk=pk, aprobado=True
    )

    # CONTAR FOTOS PARA CARRUSEL EN DETALLE
    fotos = [
        negocio.imagen_principal,
        negocio.imagen_1, negocio.imagen_2, negocio.imagen_3, negocio.imagen_4, negocio.imagen_5,
        negocio.imagen if not any([negocio.imagen_principal, negocio.imagen_1, negocio.imagen_2, negocio.imagen_3, negocio.imagen_4, negocio.imagen_5]) else None
    ]
    total_fotos = sum(1 for f in fotos if f)

    es_favorito = False
    ya_calificado = False
    form_calificacion = CalificacionForm()

    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(usuario=request.user, negocio=negocio).exists()
        ya_calificado = Calificacion.objects.filter(
            usuario=request.user,
            perfil_calificado=negocio.propietario.perfil
        ).exists()

        if request.method == 'POST' and not ya_calificado and request.user != negocio.propietario:
            form_calificacion = CalificacionForm(request.POST)
            if form_calificacion.is_valid():
                Calificacion.objects.update_or_create(
                    usuario=request.user,
                    perfil_calificado=negocio.propietario.perfil,
                    defaults={
                        'puntuacion': form_calificacion.cleaned_data['puntuacion'],
                        'comentario': form_calificacion.cleaned_data['comentario']
                    }
                )
                messages.success(request, '¡Gracias por tu calificación!')
                return redirect('negocios:detalle', pk=pk)
        else:
            form_calificacion = CalificacionForm()

    calificaciones = negocio.propietario.perfil.calificaciones_recibidas_global.select_related('usuario').order_by('-fecha')

    return render(request, 'negocios/detalle.html', {
        'negocio': negocio,
        'es_favorito': es_favorito,
        'ya_calificado': ya_calificado,
        'calificaciones': calificaciones,
        'form_calificacion': form_calificacion,
        'total_fotos': total_fotos  # NUEVO: PARA FLECHAS EN DETALLE
    })


@login_required
def toggle_favorito(request, pk):
    negocio = get_object_or_404(Negocio, pk=pk)
    favorito, created = Favorito.objects.get_or_create(usuario=request.user, negocio=negocio)
    if not created:
        favorito.delete()
        action = 'removed'
    else:
        action = 'added'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'action': action})

    messages.success(request, 'Favorito actualizado')
    return redirect('negocios:detalle', pk=pk)