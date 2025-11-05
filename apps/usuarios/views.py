# apps/usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Perfil, Calificacion  # ← AÑADIDO
from .forms import UserUpdateForm, PerfilUpdateForm, CalificacionForm  # ← AÑADIDO
from apps.negocios.models import Negocio
from apps.productos.models import Producto
from apps.servicios.models import Servicio, CategoriaServicio
# CalificacionServicio YA NO EXISTE → Se eliminó


# === REGISTRO ===
def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Perfil.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}!')
            return redirect('home:home')
        else:
            messages.error(request, 'Corrige los errores.')
    else:
        form = UserCreationForm()
    return render(request, 'usuarios/registro.html', {'form': form})


# === LOGIN ===
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Hola, {user.username}!')
            next_url = request.GET.get('next')
            return redirect(next_url or 'home:home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    return render(request, 'usuarios/login.html', {'form': form})


# === LOGOUT ===
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('home:home')


# === PERFIL ===
@login_required
def perfil(request):
    mis_negocios = Negocio.objects.filter(propietario=request.user)
    mis_servicios = Servicio.objects.filter(propietario=request.user)
    mis_productos = Producto.objects.filter(propietario=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = PerfilUpdateForm(request.POST, request.FILES, instance=request.user.perfil)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, '¡Perfil actualizado con éxito!')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = PerfilUpdateForm(instance=request.user.perfil)

    return render(request, 'usuarios/perfil.html', {
        'u_form': u_form,
        'p_form': p_form,
        'mis_negocios': mis_negocios,
        'mis_servicios': mis_servicios,
        'mis_productos': mis_productos,
    })


# === CALIFICAR PERFIL ===
@login_required
def calificar_perfil(request, perfil_id):
    perfil_calificado = get_object_or_404(Perfil, id=perfil_id)
    if request.user == perfil_calificado.user:
        messages.error(request, 'No puedes calificarte a ti mismo.')
        return redirect(request.META.get('HTTP_REFERER', 'home:home'))

    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            cal, created = Calificacion.objects.update_or_create(
                usuario=request.user,
                perfil_calificado=perfil_calificado,
                defaults={
                    'puntuacion': form.cleaned_data['puntuacion'],
                    'comentario': form.cleaned_data['comentario']
                }
            )
            messages.success(request, '¡Gracias por tu calificación!')
    return redirect(request.META.get('HTTP_REFERER', 'home:home'))