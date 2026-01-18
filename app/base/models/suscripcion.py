from django.db import models
from django.forms import ValidationError

class Suscripcion(models.Model):
    jornalero = models.ForeignKey('Jornalero', on_delete=models.CASCADE, related_name='suscripciones')
    oferta = models.ForeignKey('Oferta', on_delete=models.CASCADE, related_name='suscripciones')
    trabajo = models.BooleanField(default=False)
    activa = models.BooleanField(default=True)
    interesado = models.CharField(
        max_length=11,
        choices=[('jornalero', 'Jornalero'), ('propietario', 'Propietario')]
    )

    class Meta:
        unique_together = ('jornalero', 'oferta')

    @classmethod
    def crear(cls, jornalero, oferta, usuario_interesado):
        
        from .usuario import Jornalero, Propietario
        calendario = jornalero.getCalendario()
        periodo = oferta.getPeriodo()
        disponible = calendario.disponible(periodo.getInicio(), periodo.getFin())

        if not disponible:
            raise ValidationError("El jornalero no está disponible para esta oferta.")
        
        if isinstance(usuario_interesado, Jornalero):
            interesado = 'jornalero'
        elif isinstance(usuario_interesado, Propietario):
            interesado = 'propietario'
        elif isinstance(usuario_interesado, str):
            interesado = usuario_interesado.strip().lower()
        else:
            raise ValidationError("Usuario interesado inválido.")
        
        suscripcion = cls.objects.create(
            jornalero=jornalero,
            oferta=oferta,
            interesado=interesado
        )

        return suscripcion
    
    @classmethod
    def existe(cls, id):
        return cls.objects.filter(id=id).exists()
    
    @classmethod
    def getMatchsOferta(cls, oferta):
        return oferta.suscripciones.filter(trabajo=True)
    
    @classmethod
    def getMatchsJornalero(cls, jornalero):
        return jornalero.suscripciones.filter(trabajo=True)
    
    @classmethod
    def getSuscripcionesActivas(cls, usuario):
        return usuario.suscripciones.filter(activa=True)
    
    @classmethod
    def getLikesJornalero(cls, jornalero):
        return jornalero.suscripciones.filter(interesado='propietario', activa=True, trabajo=False)
    
    def rechazar(self, usuario):
        if (usuario == self.interesado):
            self.delete()
        else:
            self.activa = False
            self.save()

    def actualizar(self):
        self.refresh_from_db()

    def getJornalero(self):
        return self.jornalero
    
    def getOferta(self):
        return self.oferta
    
    def trabajar(self):
        self.trabajo = True
        self.oferta.restarPlaza()
        periodo = self.oferta.getPeriodo()
        self.jornalero.getCalendario().quitarPeriodo(periodo.getInicio(), periodo.getFin())
        self.save()
    
    def cancelar(self):
        self.trabajo = False
        self.save()
    
    def match(self):
        return self.trabajo
    
    def suscripcionActiva(self):
        return self.activa
    
    def getPropietario(self):
        return self.oferta.getPropietario()
    
    