from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response


# ── Utilidades ────────────────────────────────────────────────

def fetch_function(func_call: str, params=()):
    """
    Para llamar PostgreSQL para que retornen TABLE o SETOF.
    Se la consulta de  SELECT * FROM funcion(...)
    """
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {func_call}", params)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]


def fetch_query(sql: str, params=()):
    """Para consultas SQL directas."""
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]


def serialize(value):
    """Convierte Decimal y Date a tipos serializables."""
    from decimal import Decimal
    from datetime import date
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, date):
        return value.isoformat()
    return value


def clean_row(row: dict):
    return {k: serialize(v) for k, v in row.items()}


# ── Vistas ────────────────────────────────────────────────────

class ResumenGananciaView(APIView):
    def get(self, request, lote_id):
        # sp_resumen_ganancia_lote es una FUNCTION (RETURNS TABLE) → SELECT
        rows = fetch_function("sp_resumen_ganancia_lote(%s)", [lote_id])
        return Response([clean_row(r) for r in rows])


class GananciaRangoView(APIView):
    def get(self, request, lote_id):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin    = request.query_params.get('fecha_fin')
        rows = fetch_function(
            "sp_calcular_ganancia_lote(%s, %s, %s)",
            [lote_id, fecha_inicio, fecha_fin]
        )
        return Response([clean_row(r) for r in rows])


class MortalidadView(APIView):
    def get(self, request, lote_id):
        rows = fetch_query("""
            SELECT fecha,
                   cantidad_muerta,
                   SUM(cantidad_muerta) OVER (ORDER BY fecha) AS acumulado
            FROM registro_mortalidad
            WHERE lote_id = %s
            ORDER BY fecha
        """, [lote_id])
        return Response([clean_row(r) for r in rows])


class HuevosView(APIView):
    def get(self, request, lote_id):
        rows = fetch_query("""
            SELECT fecha, cantidad_huevos
            FROM registro_huevos
            WHERE lote_id = %s
            ORDER BY fecha
        """, [lote_id])
        return Response([clean_row(r) for r in rows])


class InsumosView(APIView):
    def get(self, request, lote_id):
        rows = fetch_query("""
            SELECT tipo,
                   SUM(cantidad * precio) AS costo_total,
                   COUNT(*)               AS registros
            FROM insumos_ponedora
            WHERE lotes_id = %s
            GROUP BY tipo
            ORDER BY costo_total DESC
        """, [lote_id])
        return Response([clean_row(r) for r in rows])