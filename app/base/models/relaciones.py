from django.db import models
from django.forms import ValidationError
from .ofertas import *

class Suscribir(models.Model):
    jornalero = models.ForeignKey('Jornalero', on_delete=models.CASCADE, related_name='suscripciones')
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, related_name='suscripciones')
    activa = models.BooleanField(default=True)

    class Meta:
        unique_together = ('jornalero', 'oferta')

    @classmethod
    def crear(cls, jornalero, oferta):
        if not hasattr(jornalero, 'calendario'):
            raise ValidationError("El jornalero no tiene calendario de disponibilidad.")

        calendario = jornalero.calendario
        periodo = oferta.periodo

        disponible = calendario.disponible(
            periodo.fecha_inicio.day,
            periodo.fecha_inicio.month,
            periodo.fecha_inicio.year,
            periodo.fecha_fin.day,
            periodo.fecha_fin.month,
            periodo.fecha_fin.year
        )

        if not disponible:
            raise ValidationError("El jornalero no está disponible para esta oferta.")
        
        suscripcion, existe = cls.objects.get_or_create(
            jornalero=jornalero,
            oferta=oferta,
            defaults={'activa': True}
        )

        if not existe and not suscripcion.activa:
            suscripcion.activa = True
            suscripcion.save()

        return suscripcion
    
    @classmethod
    def existe(cls, id):
        return cls.objects.filter(id=id).exists()
    
    def cancelar(self):
        self.activa = False
        self.save()

    def actualizar(self):
        self.refresh_from_db()
    
class Trabajar(models.Model):
    jornalero = models.ForeignKey('Jornalero', on_delete=models.CASCADE, related_name='trabajos')
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, related_name='trabajadores')

    class Meta:
        unique_together = ('jornalero', 'oferta')

    @classmethod
    def crear(cls, jornalero, oferta):
        if oferta.plazas == 0:
            raise ValidationError("No hay plazas disponibles para esta oferta.")

        trabajo = cls.objects.create(
            jornalero=jornalero,
            oferta=oferta
        )

        oferta.plazas -= 1
        oferta.save()
        Suscribir.objects.filter(jornalero=jornalero, oferta=oferta).update(activa=False)

        return trabajo
    
    @classmethod
    def existe(cls, id):
        return cls.objects.filter(id=id).exists()