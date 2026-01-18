from django.db import models
from django.forms import ValidationError
from django.core.validators import MinValueValidator
from ... import constants
from .periodo import Periodo
from .suscripcion import Suscripcion

class Oferta(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    plazas = models.IntegerField(validators=[MinValueValidator(0)])
    euros_hora = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(constants.MIN_EUROS_HORA)])
    periodo = models.ForeignKey(Periodo, on_delete=models.PROTECT, related_name='ofertas')
    propietario = models.ForeignKey('Propietario', on_delete=models.CASCADE, related_name='ofertas')

    def __str__(self):
        return self.titulo

    @classmethod
    def crear(cls, titulo, descripcion, plazas, eurosHora, fechaInicio, fechaFin, propietario):
        fechas = Periodo.crear(fechaInicio, fechaFin)
        oferta = cls.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            plazas=plazas,
            euros_hora=eurosHora,
            periodo=fechas,
            propietario=propietario
        )
        return oferta

    @classmethod
    def existe(cls, id):
        return cls.objects.filter(id=id).exists()
    
    @classmethod
    def getOfertasDisponibles(cls, calendario):
      ofertas = []

      for oferta in cls.objects.filter(plazas__gt=0):
          periodo_oferta = oferta.periodo
          if calendario.disponible(periodo_oferta.fecha_inicio, periodo_oferta.fecha_fin):
              ofertas.append(oferta)

      return ofertas
    
    def borrar(self):
        self.delete()

    def getPeriodo(self):
        return self.periodo
    
    def getSuscripciones(self):
        return list(self.suscripciones.all())
    
    def getPropietario(self):
        return self.propietario
    
    def restarPlaza(self):
        if self.plazas == 0:
            raise ValidationError(f"La oferta {self.id} no tiene plazas disponibles.")
        else:
            self.plazas -= 1
            self.save()

    def getPlazas(self):
        return self.plazas
    
    def getTrabajadores(self):
        trabajadores = []
        matchs = Suscripcion.getMatchsOferta(self)

        for match in matchs:
            jornalero = match.getJornalero()
            trabajadores.append(jornalero)

        return trabajadores