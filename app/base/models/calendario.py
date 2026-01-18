from django.db import models
from .periodo import Periodo
from .suscripcion import Suscripcion
from datetime import date, timedelta

class Calendario(models.Model):
    jornalero = models.OneToOneField('Jornalero', on_delete=models.CASCADE, related_name='calendario')
    periodos = models.ManyToManyField(Periodo, related_name='calendarios', blank=True)

    @classmethod
    def crear(cls, jornalero):
        if hasattr(jornalero, 'calendario'):
            jornalero.borrarCalendario()
        return cls.objects.create(jornalero=jornalero)
    
    @classmethod
    def existe(cls, id):
        return cls.objects.filter(id=id).exists()

    def disponible(self, fechaInicio, fechaFin):
        disponible = False
        for periodo in self.periodos.all():
            if periodo.disponible(fechaInicio, fechaFin):
              disponible = True
              break
        return disponible
    
    def borrar(self):
        self.delete()
    
    def incluirPeriodo(self, fechaInicio, fechaFin):
        periodo = Periodo.crear(fechaInicio, fechaFin)
        self.periodos.add(periodo)
        self.fusion()
    
    def quitarPeriodo(self, fechaInicio, fechaFin):        
        periodos = list(self.periodos.all().order_by('fecha_inicio'))

        for suscripcion in Suscripcion.getSuscripcionesActivas(self.jornalero):
            fechas = suscripcion.oferta.getPeriodo()
            if not (fechas.getFin() < fechaInicio or fechas.getInicio() > fechaFin):
                suscripcion.rechazar('jornalero')

        actualizados = []

        for periodo in periodos:
            if periodo.fecha_fin < fechaInicio:
                actualizados.append(periodo)
            elif periodo.fecha_inicio > fechaFin:
                actualizados.append(periodo)
            else:
                if periodo.fecha_inicio < fechaInicio:
                    actualizados.append(
                        Periodo.crear(
                            periodo.fecha_inicio, fechaInicio - timedelta(days=1)
                        )
                    )
                if periodo.fecha_fin > fechaFin:
                    actualizados.append(
                        Periodo.crear(
                            fechaFin + timedelta(days=1), periodo.fecha_fin
                        )
                    )

                if not periodo.enCalendario():
                    periodo.borrar()

        self.periodos.set(actualizados)
        self.save()

    def fusion(self):
        periodos = list(self.periodos.all().order_by('fecha_inicio'))
        if not periodos:
            return

        fusionados = []
        actual = periodos[0]
        for siguiente in periodos[1:]:
            if actual.fecha_fin >= (siguiente.fecha_inicio - timedelta(days=1)):
                nuevo = Periodo.crear(
                    min(actual.fecha_inicio, siguiente.fecha_inicio),
                    max(actual.fecha_fin, siguiente.fecha_fin)
                )

                for p in [actual, siguiente]:
                    if not p.enCalendario():
                        p.borrar()

                actual = nuevo
            else:
                fusionados.append(actual)
                actual = siguiente
        fusionados.append(actual)

        self.periodos.set(fusionados)
        self.save()
    
    def numeroPeriodos(self):
        return self.periodos.count()
    
    def getPeriodo(self, indice):
        periodos = list(self.periodos.all())
        if indice < 0 or indice >= len(periodos):
            raise IndexError(f"Índice {indice} fuera de rango. Hay {len(periodos)} periodos disponibles.")
        return periodos[indice]
    
    def getPeriodos(self):
        return list(self.periodos.all().order_by('fecha_inicio'))
