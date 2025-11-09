from django.db import models
from django.forms import ValidationError
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