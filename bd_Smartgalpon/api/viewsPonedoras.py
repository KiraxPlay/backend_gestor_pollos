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
    

@csrf_exempt
@api_view(['POST'])
def agregarRegistroHuevos(request):
    try:
        data = json.loads(request.body)
        with connection.cursor() as cursor:
            cursor.callproc('sp_agregar_registro_huevos', [
                data['lote_id'],
                data['fecha'],
                data['cantidad_huevos']
            ])
            result = cursor.fetchone()

        return JsonResponse({
            'success': True,
            'message': 'Registro de huevos agregado correctamente',
            'registro_id': result[0] if result else None
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    

@csrf_exempt
@api_view(['POST'])
def agregarRegistroPeso(request):
    try:
        data = json.loads(request.body)
        with connection.cursor() as cursor:
            cursor.callproc('sp_agregar_registro_peso', [
                data['lotes_id'],
                data['fecha'],
                data['peso_promedio']
            ])
            result = cursor.fetchone()

        return JsonResponse({
            'success': True,
            'message': 'Registro de peso agregado correctamente',
            'registro_id': result[0] if result else None
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    
@api_view(['POST'])
def establecerPrecioHuevo(request):
    try:
        data = json.loads(request.body)
        with connection.cursor() as cursor:
            cursor.callproc('sp_establecer_precio_huevo', [
                data['lote_id'],
                data['precio_por_huevo'],
                data['fecha_inicio']
            ])
            result = cursor.fetchone()
        
        return JsonResponse({
            'success': True,
            'message': 'Precio establecido correctamente',
            'precio_id': result[0] if result else None
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    

@api_view(['GET'])
def calcularGananciaHuevos(request, lote_id):
    try:
        # Obtener parámetros de la URL
        fecha_inicio = request.GET.get('fecha_inicio', None)
        fecha_fin = request.GET.get('fecha_fin', None)
        
        # Validar que existan los parámetros
        if not fecha_inicio or not fecha_fin:
            return JsonResponse({
                'success': False, 
                'error': 'Los parámetros fecha_inicio y fecha_fin son requeridos'
            }, status=400)
        
        with connection.cursor() as cursor:
            cursor.callproc('sp_calcular_ganancia_lote', [
                lote_id, fecha_inicio, fecha_fin
            ])
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return JsonResponse({
            'success': True,
            'lote_id': lote_id,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'ganancia': result[0] if result else {}
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    
@api_view(['GET'])
def resumenGananciaLote(request, lote_id):
  
    try:
        with connection.cursor() as cursor:
            cursor.callproc('sp_resumen_ganancia_lote', [lote_id])
            
            # Verificar si hay resultados
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                result = []
        
        if not result:
            return JsonResponse({
                'success': False,
                'error': f'Lote {lote_id} no encontrado'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'resumen': result[0]
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)