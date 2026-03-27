from django.urls import path
from .views import (
    ResumenGananciaView,
    GananciaRangoView,
    MortalidadView,
    HuevosView,
    InsumosView,
)
from .view_export import ExportarPDFView, ExportarExcelView

urlpatterns = [
    # ── Datos JSON ─────────────────────────────────────────────
    path('detalleLote/<int:lote_id>/resumen/',    ResumenGananciaView.as_view()),
    path('detalleLote/<int:lote_id>/ganancia/',   GananciaRangoView.as_view()),
    path('detalleLote/<int:lote_id>/mortalidad/', MortalidadView.as_view()),
    path('detalleLote/<int:lote_id>/huevos/',     HuevosView.as_view()),
    path('detalleLote/<int:lote_id>/insumos/',    InsumosView.as_view()),

    # ── Exportación ────────────────────────────────────────────
    path('detalleLote/<int:lote_id>/exportar/pdf/',   ExportarPDFView.as_view()),
    path('detalleLote/<int:lote_id>/exportar/excel/', ExportarExcelView.as_view()),
]