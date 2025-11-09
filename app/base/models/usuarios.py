from django.db import models
from django.forms import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from ... import constants
from .relaciones import Trabajar, Suscribir

class Usuario(models.Model):
    correo = models.EmailField(unique=True)
    usuario = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=16, blank=True, null=True, validators=[constants.phoneNumberRegex], unique=True)
    contrasena = models.CharField(max_length=128)

    class Meta:
        abstract = True
    
    @classmethod
    def crear(cls, nombre, correo, usuario, contrasena, telefono=None):
        cifrar = make_password(contrasena)
        cuenta = cls.objects.create(
            nombre=nombre,
            correo=correo,
            usuario=usuario,
            telefono=telefono,
            contrasena=cifrar
        )
        return cuenta

    def identificar(self, contrasena):
        return check_password(contrasena, self.contrasena)
    
    def eliminar(self):
        self.delete()

    @classmethod
    def existe(cls, id):
        return cls.objects.filter(id=id).exists()
    
    
class Propietario(Usuario):
    def getOfertas(self):
        return list(self.ofertas.all())
    
    def getOferta(self, indice):
        ofertas = list(self.ofertas.all())
        if indice < 0 or indice >= len(ofertas):
            raise IndexError(f"Índice {indice} fuera de rango. Hay {len(ofertas)} ofertas disponibles.")
        return ofertas[indice]
    
    def aceptarSuscripcion(self, suscripcion):
        if suscripcion.oferta.propietario != self:
            raise ValidationError("La oferta no pertenece al propietario.")
        trabajo = Trabajar.crear(suscripcion.jornalero, suscripcion.oferta)
        return trabajo        
    

class Jornalero(Usuario):
    def suscribir(self, oferta):
        suscripcion = Suscribir.crear(self, oferta)
        return suscripcion
    
    def getTrabajos(self):
        return list(self.trabajos.all())