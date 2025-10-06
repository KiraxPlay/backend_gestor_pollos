from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection

# Create your views here.
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
    re