# apps/favoritos/urls.py
from django.urls import path
from . import views

app_name = 'favoritos'

urlpatterns = [
    path('', views.mis_favoritos, name='mis_favoritos'),
]