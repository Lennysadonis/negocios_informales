from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.negocios.models import Negocio
from .models import Promocion
from .forms import PromocionForm
import hashlib
import uuid
from django.conf import settings
from django.urls import reverse

@login_required
def promocionar_negocio(request, negocio_id):
    negocio = get_object_or_404(Negocio, id=negocio_id, propietario=request.user)
    
    if request.method == 'POST':
        form = PromocionForm(request.POST)
        if form.is_valid():
            promocion = form.save(commit=False)
            promocion.negocio = negocio
            promocion.save()
            # REDIRIGIR A PAGADITOS
            return redirect('pagos:procesar_pago', promocion_id=promocion.id)
    else:
        form = PromocionForm()
    
    return render(request, 'pagos/promocionar.html', {
        'form': form,
        'negocio': negocio,
    })
    
PAGADITOS_UID = "TU_UID_AQUI"
PAGADITOS_WSK = "TU_WSK_AQUI"

def procesar_pago(request, promocion_id):
    promocion = get_object_or_404(Promocion, id=promocion_id)
    
    if promocion.pagado:
        messages.info(request, "Ya está pagado.")
        return redirect('negocios:lista')

    # PRECIO SEGÚN PLAN
    precios = {'24h': 1.00, '3d': 2.50, '7d': 5.00}
    monto = precios[promocion.plan]

    # GENERAR TOKEN
    ern = str(uuid.uuid4())
    token = hashlib.md5(f"{PAGADITOS_UID}{PAGADITOS_WSK}{ern}{monto}".encode()).hexdigest()

    context = {
        'uid': PAGADITOS_UID,
        'wsk': PAGADITOS_WSK,
        'ern': ern,
        'token': token,
        'monto': monto,
        'descripcion': f"Promoción {promocion.get_plan_display()} - {promocion.negocio.nombre}",
        'url_retorno': request.build_absolute_uri(reverse('pagos:completado')),
        'url_notificacion': request.build_absolute_uri(reverse('pagos:notificacion')),
    }
    
    return render(request, 'pagos/pagar.html', context)

def pago_completado(request):
    if request.GET.get('pg_trans_id'):
        messages.success(request, "¡Pago recibido! Tu promoción está activa.")
    else:
        messages.error(request, "Hubo un problema con el pago.")
    return redirect('home')

def notificacion_pago(request):
    # Pagaditos envía POST aquí
    if request.method == 'POST':
        trans_id = request.POST.get('pg_trans_id')
        estado = request.POST.get('pg_estado')
        if estado == 'COMPLETADO':
            # Buscar promoción por ern o trans_id
            # Marcar como pagado
            pass
    return HttpResponse("OK")