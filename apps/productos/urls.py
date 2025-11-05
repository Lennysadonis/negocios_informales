# apps/productos/urls.py
from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.lista_productos, name='lista'),
    path('publicar/', views.publicar_producto, name='publicar'),
    path('<int:pk>/', views.detalle_producto, name='detalle'),
    path('<int:pk>/favorito/', views.favorito_producto, name='favorito'),
    path('<int:pk>/borrar/', views.borrar_producto, name='borrar'),
]