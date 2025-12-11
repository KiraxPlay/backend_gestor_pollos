from ..models import Insumos


class InsumoFactory:
    @staticmethod
    def build_insumo(data):
        # Aquí podrías meter lógica especial por tipo
        if data["tipo"] == "Alimento":
            data["unidad"] = "kg"  # ejemplo: todos los alimentos van en kg
        elif data["tipo"] == "Medicamento":
            data["unidad"] = "ml"  # ejemplo: medicamentos en ml
        elif data["tipo"] == "Vacuna":
            data["unidad"] = "dosis"  # ejemplo: vacunas en dosis
        elif data["tipo"] == "Otro":
            data["unidad"] = "unidad"  # ejemplo: otros en unidades
       

        return data
