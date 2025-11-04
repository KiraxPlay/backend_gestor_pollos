import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from datetime import date

from.ponedoras import LotePonedora , InsumosPonedora , RegistroPesoPonedora , RegistroHuevos

@csrf_exempt
@api_view(['POST'])
def crearLotePonedora(request):
    try:
        data = json.loads(request.body)
        lote = LotePonedora.objects.create(
            nombre=data['nombre'],
            cantidad_gallinas=data['cantidad_gallinas'],
            precio_unitario=data['precio_unitario'],
            fecha_inicio=data['fecha_inicio'],
            cantidad_muerto=data.get('cantidad_muerto', 0),
            estado=data.get('estado', 0),
            edad_semanas=data.get('edad_semanas', 0)
        )
        return JsonResponse({'success': True, 'lote_id': lote.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@api_view(['GET'])
def detalleLotePonedora(request, lote_id):
    try:
        lote = LotePonedora.objects.get(id=lote_id)
        insumos = InsumosPonedora.objects.filter(lotes_id=lote)
        registros_peso = RegistroPesoPonedora.objects.filter(lotes_id=lote)
        registros_huevos = RegistroHuevos.objects.filter(lote=lote)

        lote_data = {
            'id': lote.id,
            'nombre': lote.nombre,
            'cantidad_gallinas': lote.cantidad_gallinas,
            'precio_unitario': str(lote.precio_unitario),
            'fecha_inicio': lote.fecha_inicio.isoformat(),
            'cantidad_muerto': lote.cantidad_muerto,
            'estado': lote.estado,
            'edad_semanas': lote.edad_semanas
        }

        insumos_data = [
            {
                'id': insumo.id,
                'nombre': insumo.nombre,
                'cantidad': insumo.cantidad,
                'unidad': insumo.unidad,
                'precio': str(insumo.precio),
                'tipo': insumo.tipo,
                'fecha': insumo.fecha.isoformat()
            } for insumo in insumos
        ]

        registros_peso_data = [
            {
                'id': registro.id,
                'fecha': registro.fecha.isoformat(),
                'peso_promedio': str(registro.peso_promedio)
            } for registro in registros_peso
        ]

        registros_huevos_data = [
            {
                'id': registro.id,
                'fecha': registro.fecha.isoformat(),
                'cantidad_huevos': registro.cantidad_huevos
            } for registro in registros_huevos
        ]

        return JsonResponse({
            'lote': lote_data,
            'insumos': insumos_data,
            'registros_peso': registros_peso_data,
            'registros_huevos': registros_huevos_data
        })
    except LotePonedora.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lote no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@api_view(['GET'])
def ListaPonedoras(request):
    try:
        lotes = LotePonedora.objects.all()
        huevos = RegistroHuevos.objects.only('cantidad_huevos')
        lotes_data = [
            {
                'id': lote.id,
                'nombre': lote.nombre,
                'cantidad_gallinas': lote.cantidad_gallinas,
                'precio_unitario': str(lote.precio_unitario),
                'fecha_inicio': lote.fecha_inicio.isoformat(),
                'cantidad_muerto': lote.cantidad_muerto,
                'estado': lote.estado,
                'edad_semanas': lote.edad_semanas,
                'huevos': [registro.cantidad_huevos for registro in huevos if registro.lote_id == lote.id]
            } for lote in lotes
        ]
        return JsonResponse({'lotes': lotes_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)