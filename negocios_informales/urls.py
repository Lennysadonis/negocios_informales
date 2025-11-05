"""
URL configuration for negocios_informales project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# negocios_informales/urls.py
# negocios_informales/urls.py
# negocios_informales/urls.py
# negocios_informales/urls.py
# negocios_informales/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.home.urls')),
    path('negocios/', include('apps.negocios.urls')),
    path('productos/', include('apps.productos.urls')),
    path('servicios/', include('apps.servicios.urls')),  # ← SIN ?
    path('usuarios/', include('apps.usuarios.urls')),
    path('contacto/', include('apps.contacto.urls')),
    path('favoritos/', include('apps.favoritos.urls')),

    # === AUTH URLs (PASSWORD CHANGE, ETC.) ===
    path('accounts/', include('django.contrib.auth.urls')),

    # === LOGIN PERSONALIZADO (SOBREESCRIBE EL DE AUTH) ===
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='usuarios/login.html'
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]

# === MEDIA EN DESARROLLO ===
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ========================================
# MEDIA EN PRODUCCIÓN (RENDER.COM)
# ========================================
# En producción, Render sirve media desde el bucket S3 o disco
# Pero puedes usar esto si usas Whitenoise + disco:
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)