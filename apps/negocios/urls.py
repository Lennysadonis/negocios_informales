# apps/negocios/urls.py
from django.urls import path
from . import views

app_name = 'negocios'

urlpatterns = [
    path('', views.lista_negocios, name='lista'),
    path('publicar/', views.publicar_negocio, name='publicar'),
    path('<int:pk>/', views.detalle_negocio, name='detalle'),
    path('<int:pk>/borrar/', views.borrar_negocio, name='borrar'),
    path('<int:pk>/favorito/', views.toggle_favorito, name='favorito'),  # ← ESTE ES EL CORRECTO
]