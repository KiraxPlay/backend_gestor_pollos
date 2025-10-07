import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection

def actualizarEstadoLote(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        p_id_lote = data.get('id_lote')
        p_nuevo_estado = data.get('1)
        
        with connection.cursor() as cursor:
            cursor.callproc('sp_actualizar_estado_lote', [p_id_lote, p_nuevo_estado])
            result = cursor.fetchall()
            
        columns = [col[0] for col in cursor.description]
        lote = [dict(zip(columns, row)) for row in result]
        
        return JsonResponse(lote, safe=False)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def crearLote(request):
    if request.metho == 'POST':
        data = json.loads(request.body)
        
        p_cantidad_pollos = data.get('cantidad_pollos')
        p_precio_unitario = data.get('precio_unitario')
        p_fecha_inicio = data.get('fecha_inicio')
        
        with connection.cursor() as cursor:
            cursor.callproc('crearLote', [p_cantidad_pollos, p_precio_unitario, p_fecha_inicio])
            result = cursor.fetchall()
            
        columns = [col[0] for col in cursor.description]
        lote = [dict(zip(columns, row)) for row in result]
        
        return JsonResponse(lote, safe=False)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def listarLotes(request):
    with connection.cursor() as cursor:
        cursor.callproc('sp_listar_lotes')
        results = cursor.fetchall()
        # Obtenemos nombres de columnas
        columns = [col[0] for col in cursor.description]

    # Convertimos a lista de diccionarios
    data = [dict(zip(columns, row)) for row in results]

    return JsonResponse(data, safe=False)