# apps/servicios/urls.py
from django.urls import path
from . import views

app_name = 'servicios'

urlpatterns = [
    path('', views.lista_servicios, name='lista'),
    path('publicar/', views.publicar_servicio, name='publicar'),
    path('<int:pk>/', views.detalle_servicio, name='detalle'),
    path('<int:pk>/borrar/', views.borrar_servicio, name='borrar'),
    path('<int:pk>/favorito/', views.toggle_favorito_servicio, name='favorito'),  # CORREGIDO
]