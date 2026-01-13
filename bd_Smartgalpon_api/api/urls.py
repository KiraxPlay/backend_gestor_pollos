from django.urls import path
from . import views


urlpatterns = [
    path('crearLote/', views.crearLote, name='crearLote'),
    path('lotes/', views.listarLotes, name='listarLotes'),
    path('eliminarLote/<int:lote_id>/', views.eliminar_lote, name='eliminar_lote'),
    path('agregarInsumo/', views.agregar_insumo, name='agregar_insumo'),
    path('detalleLote/<int:lote_id>/', views.detalle_lote, name='detalle_lote'),
    path('eliminarInsumo/<int:insumo_id>/', views.eliminar_insumo, name='eliminar_insumo'),
    path('registrarPeso/', views.registrar_peso, name='registrar_peso'),  # Nueva ruta para registrar peso
    path('historialMortalidad/<int:lote_id>/', views.historial_mortalidad, name='historial_mortalidad'),
    path('registrarMortalidad/', views.registrar_mortalidad, name='registrar_mortalidad'),
    path('detalleLote/<int:lote_id>/edad/', views.obtener_edad_lote, name='edad_lote'),
    ]
