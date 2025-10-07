from django.urls import path
from . import views

urlpatterns = [
    path('crearLote/', views.crearLote, name='crearLote'),
    path('lotes/', views.listarLotes, name='listarLotes'),
]
