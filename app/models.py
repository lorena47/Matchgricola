from django.db import models
from django.core.validators import MinValueValidator
from django.forms import ValidationError
from . import constants
from datetime import date, timedelta


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
    periodos = models.ManyToManyField(PeriodoDisponibilidad, related_name='calendarios', blank=True)

    @classmethod
    def crear(cls):
        return cls.objects.create()

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

        self.periodos.clear()
        for p in actualizados:
            self.periodos.add(p)
        self.save()

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

        self.periodos.clear()
        for p in fusionados:
            periodo = PeriodoDisponibilidad.crear(p.fecha_inicio, p.fecha_fin)
            self.periodos.add(periodo)
        self.save()


class Propietario(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    correo = models.EmailField(unique=True)

    @classmethod
    def crear(cls, nombre, correo, telefono=None):
        propietario = cls.objects.create(
            nombre=nombre,
            correo=correo,
            telefono=telefono
        )
        return propietario
    

class Jornalero(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=16, blank=True, null=True, validators=[constants.phoneNumberRegex])
    correo = models.EmailField(unique=True)
    calendario = models.OneToOneField(Calendario, on_delete=models.CASCADE, related_name='jornalero')

    @classmethod
    def crear(cls, nombre, correo, telefono=None):
        calendario = Calendario.crear()
        jornalero = cls.objects.create(
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            calendario=calendario
        )
        return jornalero
         
        
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
    