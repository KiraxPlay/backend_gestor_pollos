from django.db import models


# Modelos para la parte de gallinas ponedoras
class LotePonedora(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad_gallinas = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField()
    cantidad_muerto = models.IntegerField(default=0)
    estado = models.IntegerField(default=0)
    edad_semanas = models.IntegerField(default=0) 
    muertos_semanales = models.IntegerField(default=0)
    

    def __str__(self):
        return self.nombre
    
class RegistroHuevos(models.Model):
    lote = models.ForeignKey(LotePonedora, on_delete=models.CASCADE)
    fecha = models.DateField()
    cantidad_huevos = models.IntegerField()

    class Meta:
        db_table = 'registro_huevos'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.lote.nombre} - {self.cantidad_huevos} huevos ({self.fecha})"
    
class InsumosPonedora(models.Model):
    class TipoInsumo(models.TextChoices):
        ALIMENTO = 'Alimento'
        MEDICAMENTO = 'Medicamento'
        VACUNA = 'Vacuna'
        VITAMINA = 'Vitamina'
        DESINFECTANTE = 'Desinfectante'
        OTRO = 'Otro'
        
    lotes_id = models.ForeignKey(LotePonedora, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    unidad = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(
        max_length=20,
        choices=TipoInsumo.choices,
        default=TipoInsumo.OTRO
    )
    fecha = models.DateField()
    
    def __str__(self):
        return f"{self.nombre} - {self.tipo}"
    
class RegistroPesoPonedora(models.Model):
    lotes_id = models.ForeignKey(LotePonedora, on_delete=models.CASCADE)
    fecha = models.DateField()
    peso_promedio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Peso {self.peso_promedio} - {self.fecha}"
    

