# apps/favoritos/urls.py
from django.urls import path
from . import views

app_name = 'favoritos'

urlpatterns = [
    path('negocio/<int:negocio_id>/', views.favorito_negocio, name='negocio'),
    path('producto/<int:producto_id>/', views.favorito_producto, name='producto'),
    path('servicio/<int:servicio_id>/', views.favorito_servicio, name='servicio'),
]