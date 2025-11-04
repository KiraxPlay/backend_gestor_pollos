import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from datetime import date

from .models import Lote, Insumos, RegistroPeso, RegistroMortalidad
from .factories.factory_insumo import InsumoFactory


@csrf_exempt
@api_view(['DELETE'])
def eliminar_insumo(request, insumo_id):
    try:
        body = json.loads(request.body)  # Convierte el JSON del body a diccionario
        lote_id = body.get('lote_id')

        with connection.cursor() as cursor:
            cursor.callproc('sp_eliminar_insumo', [lote_id, insumo_id])

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def detalle_lote(request, lote_id):
    try:
        with connection.cursor() as cursor:
            cursor.callproc("sp_detalle_lote", [lote_id])

            # Primer resultado (Lote)
            result_lote = cursor.fetchall()
            columns_lote = [col[0] for col in cursor.description]
            lote_data = [dict(zip(columns_lote, row)) for row in result_lote]

            # Segundo resultado (Insumos)
            cursor.nextset()
            result_insumos = cursor.fetchall()
            columns_insumos = [col[0] for col in cursor.description]
            insumos_data = [dict(zip(columns_insumos, row)) for row in result_insumos]

            # Tercer resultado (Registros de peso)
            cursor.nextset()
            result_pesos = cursor.fetchall()
            columns_pesos = [col[0] for col in cursor.description]
            pesos_data = [dict(zip(columns_pesos, row)) for row in result_pesos]

        return JsonResponse({
            "lote": lote_data,
            "insumos": insumos_data,
            "registro_peso": pesos_data
        }, safe=False)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

@csrf_exempt
def agregar_insumo(request):
    if request.method == "POST":
        data = json.loads(request.body)

        
        insumo_data = InsumoFactory.build_insumo(data)

        try:
           
            with connection.cursor() as cursor:
                cursor.callproc(
                    "sp_agregar_insumo",
                    [
                        insumo_data["lotes_id"],
                        insumo_data["nombre"],
                        insumo_data["cantidad"],
                        insumo_data["unidad"],
                        insumo_data["precio"],
                        insumo_data["tipo"],
                        insumo_data["fecha"],
                    ]
                )
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)

@csrf_exempt
def crearLote(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            cantidad_pollos = data.get("cantidad_pollos")
            precio_unitario = data.get("precio_unitario")
            fecha_inicio = data.get("fecha_inicio")  # formato: "2025-10-06"
            edad_lote = 0

            with connection.cursor() as cursor:
                cursor.callproc("sp_crear_nuevo_lote", [cantidad_pollos, precio_unitario, fecha_inicio])
                result = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                lote_data = [dict(zip(columns, row)) for row in result]

            return JsonResponse({"success": True, "lote": lote_data}, safe=False)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)

def listarLotes(request):
    with connection.cursor() as cursor:
        cursor.callproc('sp_listar_lotes')
        results = cursor.fetchall()
        # Obtenemos nombres de columnas
        columns = [col[0] for col in cursor.description]

    # Convertimos a lista de diccionarios
    data = [dict(zip(columns, row)) for row in results]

    return JsonResponse(data, safe=False)

@csrf_exempt
def registrar_peso(request):
    if request.method == 'POST':
        try:
            # Leer datos desde JSON
            data = json.loads(request.body)
            lotes_id = data.get('lotes_id')
            peso_promedio = data.get('peso_promedio')
            fecha = date.today()

            # Validar que no sean nulos
            if not lotes_id or not peso_promedio:
                return JsonResponse({'error': 'Faltan datos obligatorios'}, status=400)

            # Llamar al procedimiento almacenado
            with connection.cursor() as cursor:
                cursor.callproc('sp_registrar_peso', [lotes_id, fecha, peso_promedio])

            return JsonResponse({'message': 'Peso registrado correctamente'}, status=201)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def registrar_mortalidad(request):
    """Registra nueva mortalidad - el trigger se encarga del registro"""
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            lote_id = data.get('lote_id')
            cantidad_muerta = data.get('cantidad_muerta')

            if not lote_id or cantidad_muerta is None:
                return JsonResponse({'error': 'Datos incompletos'}, status=400)

            # Solo actualizamos lote.cantidad_muerto - el trigger hará el registro
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE lote 
                    SET cantidad_muerto = cantidad_muerto + %s
                    WHERE id = %s
                """, [cantidad_muerta, lote_id])
                
                # Verificar que se actualizó alguna fila
                if cursor.rowcount == 0:
                    return JsonResponse({'error': 'Lote no encontrado'}, status=404)

            return JsonResponse({'message': 'Mortalidad registrada correctamente'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def historial_mortalidad(request, lote_id):
    """Obtiene el historial de mortalidad para un lote específico"""
    if request.method == 'GET':
        try:
            # Verificar que el lote existe
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, nombre, cantidad_muerto FROM lote WHERE id = %s", [lote_id])
                lote = cursor.fetchone()
                
                if not lote:
                    return JsonResponse({'error': 'Lote no encontrado'}, status=404)

            # Obtener el historial de mortalidad desde la tabla registro_mortalidad
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, fecha, cantidad_muerta 
                    FROM registro_mortalidad 
                    WHERE lote_id = %s 
                    ORDER BY fecha DESC
                """, [lote_id])
                
                registros = cursor.fetchall()
            
            # Formatear la respuesta
            historial_data = []
            for registro in registros:
                historial_data.append({
                    'id': registro[0],
                    'fecha': registro[1].strftime('%Y-%m-%d') if registro[1] else None,
                    'cantidad_muerta': registro[2]
                })
            
            return JsonResponse({
                'lote_id': lote_id,
                'lote_nombre': lote[1],
                'cantidad_muerto_total': lote[2],
                'historial': historial_data
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def obtener_edad_lote(request, lote_id):
    """Obtiene específicamente la edad_dias de un lote usando conexión directa"""
    if request.method == 'GET':
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, nombre, edad_dias FROM lote WHERE id = %s", [lote_id])
                lote = cursor.fetchone()
                
                if not lote:
                    return JsonResponse({'error': 'Lote no encontrado'}, status=404)
                
                return JsonResponse({
                    'lote_id': lote[0],
                    'nombre': lote[1], 
                    'edad_dias': lote[2]  # Del trigger
                })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)
