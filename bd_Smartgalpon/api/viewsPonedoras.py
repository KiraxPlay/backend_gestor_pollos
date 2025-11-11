import json
from django.shortcuts import render
from django.db import connection
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
        with connection.cursor() as cursor:
            cursor.callproc('crear_lote_ponedora', [
                data['cantidad_gallinas'],
                data['precio_unitario'],
                data['fecha_inicio']
            ])
            result = cursor.fetchone()

        return JsonResponse({
            'success': True,
            'message': 'Lote creado correctamente',
            'lote_id': result[0] if result else None,
            'nombre_lote': result[1] if result else None
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

    
@api_view(['GET'])
def detalleLotePonedora(request, lote_id):
    try:
        with connection.cursor() as cursor:
            # Llamamos a un SP que devuelva varios resultados
            cursor.callproc('sp_detalle_lote_ponedora', [lote_id])

            # Django no soporta múltiples conjuntos de resultados directamente,
            # pero puedes obtener cada uno con cursor.nextset()
            lote_data = []
            insumos_data = []
            registros_peso_data = []
            registros_huevos_data = []

            # Primer conjunto → Lote
            columns = [col[0] for col in cursor.description]
            lote_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Siguiente conjunto → Insumos
            cursor.nextset()
            columns = [col[0] for col in cursor.description]
            insumos_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Siguiente conjunto → Registros de peso
            cursor.nextset()
            columns = [col[0] for col in cursor.description]
            registros_peso_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Siguiente conjunto → Registros de huevos
            cursor.nextset()
            columns = [col[0] for col in cursor.description]
            registros_huevos_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        if not lote_data:
            return JsonResponse({'success': False, 'error': 'Lote no encontrado'}, status=404)

        return JsonResponse({
            'success': True,
            'lote': lote_data[0],
            'insumos': insumos_data,
            'registros_peso': registros_peso_data,
            'registros_huevos': registros_huevos_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@api_view(['GET'])
def ListaPonedoras(request):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('sp_listar_lotes_ponedoras')
            columns = [col[0] for col in cursor.description]
            lotes = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return JsonResponse({'success': True, 'lotes': lotes})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    
@csrf_exempt
@api_view(['POST'])
def agregarInsumoPonedora(request):
    try:
        data = json.loads(request.body)
        with connection.cursor() as cursor:
            cursor.callproc('sp_agregar_insumo_ponedora', [
                data['lotes_id'],
                data['nombre'],
                data['cantidad'],
                data['unidad'],
                data['precio'],
                data['tipo'],
                data['fecha']
            ])
            result = cursor.fetchone()

        return JsonResponse({
            'success': True,
            'message': 'Insumo agregado correctamente',
            'insumo_id': result[0] if result else None
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)