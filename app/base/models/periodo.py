from django.db import models
from django.forms import ValidationError

class Periodo(models.Model):
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    class Meta:
        unique_together = ('fecha_inicio', 'fecha_fin')

    @classmethod
    def crear(cls, fechaInicio, fechaFin):
        if fechaInicio > fechaFin:
            raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")

        periodo, _ = cls.objects.get_or_create(
            fecha_inicio=fechaInicio,
            fecha_fin=fechaFin
        )
        
        return periodo
    
    @classmethod
    def existe(cls, id):
        return cls.objects.filter(id=id).exists()
    
    def disponible(self, fechaInicio, fechaFin):
        return self.fecha_inicio <= fechaInicio and fechaFin <= self.fecha_fin
    
    def enCalendario(self):
        return self.calendarios.exists()
    
    def borrar(self):
        if self.enCalendario():
            raise ValidationError(f"El periodo {self.id} está en uso en un calendario y no puede borrarse.")
        self.delete()

    def getInicio(self):
        return self.fecha_inicio
    
    def getFin(self):
        return self.fecha_fin