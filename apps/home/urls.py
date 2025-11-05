from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='home'),
    path('explora/', views.explora, name='explora'),  # ← VISTA CORRECTA
]