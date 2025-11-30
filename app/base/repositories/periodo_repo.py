import logging
from django.core.exceptions import ValidationError
from ..models.periodo import Periodo

logger = logging.getLogger('periodo')

class PeriodoRepository:

    @staticmethod
    def crear(fecha_inicio, fecha_fin):
        try:
            periodo = Periodo.crear(fecha_inicio, fecha_fin)
            logger.info(f"Periodo creado: {periodo.id} ({fecha_inicio} → {fecha_fin})")
            return periodo
        except ValidationError as e:
            logger.warning(f"No se pudo crear periodo ({fecha_inicio} → {fecha_fin}): {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creando periodo ({fecha_inicio} → {fecha_fin}): {str(e)}")
            raise

    @staticmethod
    def existe(periodo_id):
        try:
            return Periodo.existe(periodo_id)
        except Exception as e:
            logger.error(f"Error verificando existencia de periodo {periodo_id}: {str(e)}")
            raise

    @staticmethod
    def borrar(periodo):
        try:
            id = periodo.id
            periodo.borrar()
            logger.info(f"Periodo {id} borrado")
        except ValidationError as e:
            logger.warning(f"No se puede borrar periodo {periodo.id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error borrando periodo {periodo.id}: {str(e)}")
            raise

    @staticmethod
    def disponible(periodo, fecha_inicio, fecha_fin):
        try:
            return periodo.disponible(fecha_inicio, fecha_fin)
        except Exception as e:
            logger.error(f"Error verificando la disponibilidad en periodo {periodo.id} ({fecha_inicio} → {fecha_fin}): {str(e)}")
            raise

    @staticmethod
    def enCalendario(periodo):
        try:
            return periodo.enCalendario()
        except Exception as e:
            logger.error(f"Error verificando si el periodo {periodo.id} está en algún calendario: {str(e)}")
            raise

    @staticmethod
    def getInicio(periodo):
        try:
            return periodo.getInicio()
        except Exception as e:
            logger.error(f"Error obteniendo la fecha de inicio del periodo {periodo.id}: {str(e)}")
            raise

    @staticmethod
    def getFin(periodo):
        try:
            return periodo.getFin()
        except Exception as e:
            logger.error(f"Error obteniendo fecha de fin del periodo {periodo.id}: {str(e)}")
            raise
