from django.db import models
from django.forms import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from ... import constants
from .calendario import Calendario
from .suscripcion import Suscripcion
from .oferta import Oferta

class Usuario(models.Model):
    usuario = models.CharField(max_length=50, primary_key=True)
    contrasenia = models.CharField(max_length=128)
    correo = models.EmailField(unique=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=16, blank=True, null=True, validators=[constants.phoneNumberRegex])

    def __str__(self):
        return self.usuario

    class Meta:
        abstract = True
    
    @classmethod
    def crear(cls, usuario, nombre, correo, contrasenia, telefono=None):
        cifrar = make_password(contrasenia)
        cuenta = cls.objects.create(
            usuario=usuario,
            contrasenia=cifrar,
            correo=correo,
            nombre=nombre,
            telefono=telefono
        )
        return cuenta
    
    @classmethod
    def existe(cls, usuario):
        return cls.objects.filter(usuario=usuario).exists()

    def identificar(self, contrasenia):
        return check_password(contrasenia, self.contrasenia)
    
    def borrar(self):
        self.delete()
    
    
class Propietario(Usuario):
    def getOfertas(self):
        return list(self.ofertas.all())
    
    def getOferta(self, indice):
        ofertas = list(self.ofertas.all())
        if indice < 0 or indice >= len(ofertas):
            raise IndexError(f"Índice {indice} fuera de rango. Hay {len(ofertas)} ofertas disponibles.")
        return ofertas[indice]       
    
    def proponer(self, oferta, jornalero):
        suscripcion = Suscripcion.crear(jornalero, oferta, self)
        return suscripcion
    
    def aceptarSuscripcion(self, suscripcion):
        if suscripcion.getOferta().getPropietario() != self:
            raise ValidationError(f"La oferta {suscripcion.getOferta().id} no pertenece al propietario {self.usuario} (no la puede aceptar).")
        else:
            suscripcion.trabajar()

    def getJornalerosDisponibles(self):
        disponiblesPorOferta = {}

        for oferta in self.ofertas.all():
            periodo = oferta.getPeriodo()
            disponibles = Jornalero.getJornalerosDisponibles(periodo)
            disponiblesPorOferta[oferta] = disponibles

        return disponiblesPorOferta
    
    def cancelarSuscripcion(self, suscripcion):
        if (suscripcion.getPropietario() == self):
            suscripcion.rechazar('propietario')
        else:
            raise ValidationError(f"La suscripción {suscripcion.id} no pertenece al propietario {self.usuario} (no la puede cancelar).")
        
    def getTrabajos(self):
        trabajos = {}

        for oferta in self.ofertas.all():
            matchs = Suscripcion.getMatchsOferta(oferta)
            jornaleros = [m.getJornalero() for m in matchs]
            trabajos[oferta] = jornaleros

        return trabajos

class Jornalero(Usuario):
    def tenerCalendario(self):
        Calendario.crear(self)

    def borrarCalendario(self):
        if hasattr(self, 'calendario'):
            self.calendario.delete()

    def getCalendario(self):
        return self.calendario
    
    def suscribir(self, oferta):
        suscripcion = Suscripcion.crear(self, oferta, self)
        return suscripcion
    
    def getOfertasDisponibles(self):
        ofertas_disponibles = []

        calendario = self.getCalendario()

        for oferta in Oferta.objects.all():
            periodo = oferta.getPeriodo()
            if not calendario.disponible(periodo.getInicio(), periodo.getFin()):
                continue

            if Suscripcion.objects.filter(
                jornalero=self,
                oferta=oferta
            ).exists():
                continue

            ofertas_disponibles.append(oferta)

        return ofertas_disponibles
    
    def cancelarSuscripcion(self, suscripcion):
        if (suscripcion.getJornalero() == self):
            suscripcion.rechazar('jornalero')
        else:
            raise ValidationError(f"La suscripción {suscripcion.id} no pertenece al jornalero {self.usuario} (no la puede cancelar).")
        
    def getTrabajos(self):
        trabajos = []
        matchs = Suscripcion.getMatchsJornalero(self)

        for match in matchs:
            oferta = match.getOferta()
            trabajos.append(oferta)

        return trabajos
    
    def getPropuestas(self):
        return Suscripcion.getLikesJornalero(self)
    
    def aceptarPropuesta(self, suscripcion):
        if suscripcion.getJornalero() != self:
            raise ValidationError(f"La oferta {suscripcion.getOferta().id} no pertenece al jornalero {self.usuario} (no la puede aceptar).")
        else:
            suscripcion.trabajar()
    
    @classmethod
    def getJornalerosDisponibles(cls, periodo):
        jornaleros = []

        ofertas = Oferta.objects.filter(periodo=periodo)

        for jornalero in cls.objects.all():

            if Suscripcion.objects.filter(
                jornalero=jornalero,
                oferta__in=ofertas
            ).exists():
                continue

            calendario = jornalero.getCalendario()
            if calendario.disponible(
                periodo.getInicio(),
                periodo.getFin()
            ):
                jornaleros.append(jornalero)

        return jornaleros