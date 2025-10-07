import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
import json
from django.http import JsonResponse
from django.db import connection
from rest_framework.decorators import api_view

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
        # Extraer datos del body (ejemplo con JSON)
        import json
        data = json.loads(request.body)

        p_lotes_id = data.get("lotes_id")
        p_nombre = data.get("nombre")
        p_cantidad = data.get("cantidad")
        p_unidad = data.get("unidad")
        p_precio = data.get("precio")
        p_tipo = data.get("tipo")
        p_fecha = data.get("fecha")

        try:
            with connection.cursor() as cursor:
                cursor.callproc("sp_agregar_insumo", [
                    p_lotes_id, p_nombre, p_cantidad, p_unidad,
                    p_precio, p_tipo, p_fecha
                ])

                # Para obtener el resultado del SELECT final del SP
                result = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                data_result = [dict(zip(columns, row)) for row in result]

            return JsonResponse({"success": True, "insumo": data_result}, safe=False)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
def crearLote(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            cantidad_pollos = data.get("cantidad_pollos")
            precio_unitario = data.get("precio_unitario")
            fecha_inicio = data.get("fecha_inicio")  # formato: "2025-10-06"

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