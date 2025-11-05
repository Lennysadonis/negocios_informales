from django.urls import path
from . import views

urlpatterns = [
    path('promocionar/negocio/<int:negocio_id>/', views.promocionar_negocio, name='promocionar_negocio'),
    path('promocionar/producto/<int:producto_id>/', views.promocionar_producto, name='promocionar_producto'),
    path('webhook/', views.pagadito_webhook, name='pagadito_webhook'),
]