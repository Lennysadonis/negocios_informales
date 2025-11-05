from django.urls import path
from . import views

app_name = 'chat_pro'   # ← ÚNICO EN TODO EL PROYECTO

urlpatterns = [
    path('', views.mensajes, name='mensajes'),
    path('con/<int:user_id>/', views.chat_room, name='chat_room'),
]