from django.urls import path
from . import viewsPonedoras


urlpatterns = [    path('crearLotePonedora/', viewsPonedoras.crearLotePonedora, name='crearLotePonedora'),
                   path('detalleLotePonedora/<int:lote_id>/', viewsPonedoras.detalleLotePonedora, name='detalleLotePonedora'),
                   path('lotesPonedoras/', viewsPonedoras.ListaPonedoras, name='ListaPonedoras'),
                   path('agregarInsumo/', viewsPonedoras.agregarInsumoPonedora, name='agregarInsumoPonedora'),
                   path('eliminarInsumoPonedora/<int:insumo_id>/', viewsPonedoras.eliminarInsumoPonedora, name='eliminarInsumoPonedora'),
                   path('registroHuevos/', viewsPonedoras.agregarRegistroHuevos, name='agregarRegistroHuevos'),
                   path('registroPesoPonedora/', viewsPonedoras.agregarRegistroPeso, name='agregarRegistroPesoPonedora'),
                   path('precioVentaHuevos/', viewsPonedoras.establecerPrecioHuevo, name='obtenerPrecioVentaHuevos'),
                   path('calcularGanaciasHuevos/<int:lote_id>/', viewsPonedoras.calcularGananciaHuevos, name='calcularGananciasHuevos'),
                   path('resumenGanancias/<int:lote_id>/', viewsPonedoras.resumenGananciaLote, name='resumenGananciasHuevos'),
                   path('eliminarLotePonedora/<int:lote_id>/', viewsPonedoras.eliminarLotePonedora, name='eliminarLotePonedora'),
]