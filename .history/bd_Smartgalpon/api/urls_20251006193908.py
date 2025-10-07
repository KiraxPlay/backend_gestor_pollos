from django.urls import path
from . import views

urlpatterns = [
    path('crearLote/', views.crearLote, name='crearLote'),
    path('lotes/', views.listarLotes, name='listarLotes'),
    path('agregarInsumo/', views.agregar_insumo, name='agregar_insumo'),
    path('detalleLote/<int:lote_id>/', views.detalle_lote, name='detalle_lote'),
    path('eliminarInsumo/<int:insumo_id>/', views.eliminar_insumo, name='eliminar_insumo'),
]
