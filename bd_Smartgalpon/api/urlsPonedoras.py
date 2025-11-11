from django.urls import path
from . import viewsPonedoras


urlpatterns = [    path('crearLotePonedora/', viewsPonedoras.crearLotePonedora, name='crearLotePonedora'),
                   path('detalleLotePonedora/<int:lote_id>/', viewsPonedoras.detalleLotePonedora, name='detalleLotePonedora'),
                   path('lotesPonedoras/', viewsPonedoras.ListaPonedoras, name='ListaPonedoras'),
                   path('agregarInsumo/', viewsPonedoras.agregarInsumoPonedora, name='agregarInsumoPonedora'),
]