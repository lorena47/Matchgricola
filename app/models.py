from django.db import models
from django.core.validators import MinValueValidator
from django.forms import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from . import constants
from datetime import date, timedelta
from .models import *


class PeriodoDisponibilidad(models.Model):
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    @classmethod
    def crear(cls, *args):
        if len(args) == 6:
            diaInicio, mesInicio, anoInicio, diaFin, mesFin, anoFin = args
            fechaInicio = date(anoInicio, mesInicio, diaInicio)
            fechaFin = date(anoFin, mesFin, diaFin)
        elif len(args) == 2:
            fechaInicio, fechaFin = args
        else:
            raise ValueError("Se deben pasar 2 fechas o 6 números (día, mes, año)")

        if fechaInicio > fechaFin:
            raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")

        periodo, _ = cls.objects.get_or_create(
            fecha_inicio=fechaInicio,
            fecha_fin=fechaFin
        )
        return periodo
    
    def disponible(self, fechaInicio, fechaFin):
        return self.fecha_inicio <= fechaInicio and fechaFin <= self.fecha_fin
    

class Calendario(models.Model):
    jornalero = models.OneToOneField('Jornalero', on_delete=models.CASCADE, related_name='calendario')
    periodos = models.ManyToManyField(PeriodoDisponibilidad, related_name='calendarios', blank=True)

    @classmethod
    def crear(cls, jornalero):
        if hasattr(jornalero, 'calendario'):
            jornalero.calendario.delete()
        return cls.objects.create(jornalero=jornalero)

    def incluirPeriodo(self, diaInicio, mesInicio, anoInicio, diaFin, mesFin, anoFin):
        periodo = PeriodoDisponibilidad.crear(diaInicio, mesInicio, anoInicio, diaFin, mesFin, anoFin)
        self.periodos.add(periodo)
        Calendario.fusion(self)

    def disponible(self, diaInicio, mesInicio, anoInicio, diaFin, mesFin, anoFin):
        fechaInicio = date(anoInicio, mesInicio, diaInicio)
        fechaFin = date(anoFin, mesFin, diaFin)
        disponible = False
        for periodo in self.periodos.all():
            if periodo.disponible(fechaInicio, fechaFin):
              disponible = True
              break
        return disponible
    
    def quitarPeriodo(self, diaInicio, mesInicio, anoInicio, diaFin, mesFin, anoFin):
        fechaInicio = date(anoInicio, mesInicio, diaInicio)
        fechaFin = date(anoFin, mesFin, diaFin)
        
        periodos = list(self.periodos.all().order_by('fecha_inicio'))
        actualizados = []

        for periodo in periodos:
            if periodo.fecha_fin < fechaInicio:
                actualizados.append(periodo)
            elif periodo.fecha_inicio > fechaFin:
                actualizados.append(periodo)
            else:
                if periodo.fecha_inicio < fechaInicio:
                    actualizados.append(
                        PeriodoDisponibilidad.crear(
                            periodo.fecha_inicio, fechaInicio - timedelta(days=1)
                        )
                    )
                if periodo.fecha_fin > fechaFin:
                    actualizados.append(
                        PeriodoDisponibilidad.crear(
                            fechaFin + timedelta(days=1), periodo.fecha_fin
                        )
                    )

        self.periodos.set(actualizados)
        self.save()

        for suscripcion in self.jornalero.suscripciones.filter(activa=True).select_related('oferta__periodo'):
            oferta = suscripcion.oferta
            periodo_oferta = oferta.periodo
            if not self.disponible(
                periodo_oferta.fecha_inicio.day,
                periodo_oferta.fecha_inicio.month,
                periodo_oferta.fecha_inicio.year,
                periodo_oferta.fecha_fin.day,
                periodo_oferta.fecha_fin.month,
                periodo_oferta.fecha_fin.year
            ):
                suscripcion.activa = False
                suscripcion.save()

    def fusion(self):
        periodos = list(self.periodos.all().order_by('fecha_inicio'))
        if not periodos:
            return

        fusionados = []
        actual = periodos[0]
        for siguiente in periodos[1:]:
            if actual.fecha_fin >= (siguiente.fecha_inicio - timedelta(days=1)):
                actual = PeriodoDisponibilidad.crear(
                    min(actual.fecha_inicio, siguiente.fecha_inicio),
                    max(actual.fecha_fin, siguiente.fecha_fin)
                )
            else:
                fusionados.append(actual)
                actual = siguiente
        fusionados.append(actual)

        nuevos_periodos = [PeriodoDisponibilidad.crear(p.fecha_inicio, p.fecha_fin) for p in fusionados]
        self.periodos.set(nuevos_periodos)
        self.save()

    @classmethod
    def existe(cls, id):
        return cls.objects.filter(id=id).exists()
    
    def numeroPeriodos(self):
        return self.periodos.count()
    
    def getPeriodo(self, indice):
        periodos = list(self.periodos.all())
        if indice < 0 or indice >= len(periodos):
            raise IndexError(f"Índice {indice} fuera de rango. Hay {len(periodos)} periodos disponibles.")
        return periodos[indice]
    

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


class Oferta(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    plazas = models.IntegerField(validators=[MinValueValidator(0)])
    euros_hora = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(constants.MIN_EUROS_HORA)])
    periodo = models.ForeignKey(PeriodoDisponibilidad, on_delete=models.PROTECT, related_name='ofertas')
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name='ofertas')

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
    
    def getSuscripciones(self):
        return list(self.suscripciones.all())
    
    def getTrabajadores(self):
        return list(self.trabajadores.all())

    
##################################################################################################
# MODELOS DE RELACIONES
##################################################################################################

class Suscribir(models.Model):
    jornalero = models.ForeignKey(Jornalero, on_delete=models.CASCADE, related_name='suscripciones')
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
    jornalero = models.ForeignKey(Jornalero, on_delete=models.CASCADE, related_name='trabajos')
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


##################################################################################################
## FUNCIONES FLUJO
##################################################################################################

def obtenerOfertasDisponibles(jornalero):
    if not hasattr(jornalero, 'calendario'):
        return []

    calendario = jornalero.calendario
    ofertas = []

    for oferta in Oferta.objects.filter(plazas__gt=0):
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