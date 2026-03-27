from rest_framework.views import APIView
from .exports import exportar_pdf, exportar_excel

# para exportar a pdf
class ExportarPDFView(APIView):
    def get(self, request, lote_id):
        return exportar_pdf(lote_id)


# para exportar a excel
class ExportarExcelView(APIView):
    def get(self, request, lote_id):
        return exportar_excel(lote_id)