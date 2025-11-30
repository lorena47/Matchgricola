import logging
from ..models.calendario import Calendario

logger = logging.getLogger('calendario')

class CalendarioRepository:

    @staticmethod
    def crear(jornalero):
        try:
            calendario = Calendario.crear(jornalero)
            logger.info(f"Calendario creado para jornalero {jornalero.usuario}")
            return calendario
        except Exception as e:
            logger.error(f"Error creando calendario para {jornalero.usuario}: {str(e)}")
            raise

    @staticmethod
    def existe(calendario_id):
        try:
            return Calendario.existe(calendario_id)
        except Exception as e:
            logger.error(f"Error verificando existencia de calendario {calendario_id}: {str(e)}")
            raise

    @staticmethod
    def borrar(calendario):
        try:
            calendario.borrar()
            logger.info(f"Calendario {calendario.id} borrado")
        except Exception as e:
            logger.error(f"Error borrando calendario {calendario.id}: {str(e)}")
            raise

    @staticmethod
    def incluirPeriodo(calendario, fecha_inicio, fecha_fin):
        try:
            calendario.incluirPeriodo(fecha_inicio, fecha_fin)
            logger.info(f"Periodo {fecha_inicio} → {fecha_fin} incluido en el calendario {calendario.id}")
        except Exception as e:
            logger.error(f"Error incluyendo periodo en el calendario {calendario.id}: {str(e)}")
            raise

    @staticmethod
    def quitarPeriodo(calendario, fecha_inicio, fecha_fin):
        try:
            calendario.quitarPeriodo(fecha_inicio, fecha_fin)
            logger.info(f"Periodo {fecha_inicio} → {fecha_fin} quitado del calendario {calendario.id}")
        except Exception as e:
            logger.error(f"Error quitando periodo del calendario {calendario.id}: {str(e)}")
            raise
