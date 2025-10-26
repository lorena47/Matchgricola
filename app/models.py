from django.db import models
from django.core.validators import MinValueValidator
from . import constants
from datetime import date

class PeriodoDisponibilidad(models.Model):
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    @classmethod
    def crear(cls, diaInicio, mesInicio, añoInicio, diaFin, mesFin, añoFin):
        fechaInicio = date(añoInicio, mesInicio, diaInicio)
        fechaFin = date(añoFin, mesFin, diaFin)
        periodo, _ = cls.objects.get_or_create(
            fecha_inicio=fechaInicio,
            fecha_fin=fechaFin
        )
        return periodo
    
    def disponible(self, fechaInicio, fechaFin):
        return self.fecha_inicio <= fechaInicio and fechaFin <= self.fecha_fin
    
class Oferta(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    plazas = models.IntegerField(validators=[MinValueValidator(0)])
    euros_hora = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(constants.MIN_EUROS_HORA)])
    periodo = models.ForeignKey(PeriodoDisponibilidad, on_delete=models.PROTECT, related_name='ofertas')

    @classmethod
    def crear(cls, titulo, descripcion, 
              diaInicio, mesInicio, añoInicio,
              diaFin, mesFin, añoFin, 
              plazas, eurosHora):
        fechas = PeriodoDisponibilidad.crear(diaInicio, mesInicio, añoInicio, diaFin, mesFin, añoFin)
        oferta = cls.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            plazas=plazas,
            euros_hora=eurosHora,
            periodo=fechas
        )
        return oferta

class Calendario(models.Model):
    periodos = models.ManyToManyField(PeriodoDisponibilidad, related_name='calendarios', blank=True)

    @classmethod
    def crear(cls):
        return cls.objects.create()

    def incluirPeriodo(self, diaInicio, mesInicio, añoInicio, diaFin, mesFin, añoFin):
        periodo = PeriodoDisponibilidad.crear(diaInicio, mesInicio, añoInicio, diaFin, mesFin, añoFin)
        self.periodos.add(periodo)

    def disponible(self, diaInicio, mesInicio, añoInicio, diaFin, mesFin, añoFin):
        fechaInicio = date(añoInicio, mesInicio, diaInicio)
        fechaFin = date(añoFin, mesFin, diaFin)
        disponible = False
        for periodo in self.periodos.all():
            if periodo.disponible(fechaInicio, fechaFin):
              disponible = True
              break
        return disponible
