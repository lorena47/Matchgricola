from django.db import models
from django.core.validators import MinValueValidator
from ... import constants
from .calendarios import *

class Oferta(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    plazas = models.IntegerField(validators=[MinValueValidator(0)])
    euros_hora = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(constants.MIN_EUROS_HORA)])
    periodo = models.ForeignKey(PeriodoDisponibilidad, on_delete=models.PROTECT, related_name='ofertas')
    propietario = models.ForeignKey('Propietario', on_delete=models.CASCADE, related_name='ofertas')

    @classmethod
    def crear(cls, titulo, descripcion, 
              diaInicio, mesInicio, anoInicio,
              diaFin, mesFin, anoFin, 
              eurosHora, propietario, plazas=1):
        fechas = PeriodoDisponibilidad.crear(diaInicio, mesInicio, anoInicio, diaFin, mesFin, anoFin)
        oferta = cls.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            plazas=plazas,
            euros_hora=eurosHora,
            periodo=fechas,
            propietario=propietario
        )
        return oferta
    
    def eliminar(self):
        self.delete()

    @classmethod
    def existe(cls, id):
        return cls.objects.filter(id=id).exists()
    
    @classmethod
    def obtenerOfertasDisponibles(cls, jornalero):
      if not hasattr(jornalero, 'calendario'):
          return []

      calendario = jornalero.calendario
      ofertas = []

      for oferta in cls.objects.filter(plazas__gt=0):
          periodo_oferta = oferta.periodo
          if calendario.disponible(
              periodo_oferta.fecha_inicio.day,
              periodo_oferta.fecha_inicio.month,
              periodo_oferta.fecha_inicio.year,
              periodo_oferta.fecha_fin.day,
              periodo_oferta.fecha_fin.month,
              periodo_oferta.fecha_fin.year
          ):
              ofertas.append(oferta)

      return ofertas
    
    def getSuscripciones(self):
        return list(self.suscripciones.all())
    
    def getTrabajadores(self):
        return list(self.trabajadores.all())