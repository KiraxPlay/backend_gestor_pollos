from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('crearLote/', views.crearLote, name='crearLote'),
    path('lotes/', views.listarLotes, name='listarLotes'),
]
