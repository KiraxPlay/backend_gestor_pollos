import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection





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