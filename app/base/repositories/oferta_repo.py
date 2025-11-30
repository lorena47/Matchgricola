import logging
from django.core.exceptions import ValidationError
from ..models.oferta import Oferta

logger = logging.getLogger('oferta')

class OfertaRepository:

    @staticmethod
    def crear(titulo, descripcion, plazas, eurosHora, fechaInicio, fechaFin, propietario):
        try:
            oferta = Oferta.crear(titulo, descripcion, plazas, eurosHora, fechaInicio, fechaFin, propietario)
            logger.info(f"Oferta {oferta.id} creada por propietario {propietario.usuario}")
            return oferta
        except Exception as e:
            logger.error(f"Error creando oferta: {str(e)}")
            raise

    @staticmethod
    def existe(oferta_id):
        try:
            return Oferta.existe(oferta_id)
        except Exception as e:
            logger.error(f"Error verificando existencia de oferta {oferta_id}: {str(e)}")
            raise

    @staticmethod
    def borrar(oferta):
        try:
            oferta.borrar()
            logger.info(f"Oferta {oferta.id} borrada")
        except Exception as e:
            logger.error(f"Error borrando oferta {oferta.id}: {str(e)}")
            raise

    @staticmethod
    def getPeriodo(oferta):
        try:
            return oferta.getPeriodo()
        except Exception as e:
            logger.error(f"Error obteniendo el periodo de la oferta {oferta.id}: {str(e)}")
            raise

    @staticmethod
    def getPropietario(oferta):
        try:
            return oferta.getPropietario()
        except Exception as e:
            logger.error(f"Error obteniendo el propietario de la oferta {oferta.id}: {str(e)}")
            raise

    @staticmethod
    def restarPlaza(oferta):
        try:
            oferta.restarPlaza()
            logger.info(f"Plaza restada en oferta {oferta.id}. Plazas restantes: {oferta.getPlazas()}")
        except ValidationError as e:
            logger.warning(f"No se pudo restar plaza en oferta {oferta.id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error restando plaza en oferta {oferta.id}: {str(e)}")
            raise

    @staticmethod
    def getPlazas(oferta):
        try:
            return oferta.getPlazas()
        except Exception as e:
            logger.error(f"Error obteniendo las plazas de oferta {oferta.id}: {str(e)}")
            raise

    @staticmethod
    def getTrabajadores(oferta):
        try:
            return oferta.getTrabajadores()
        except Exception as e:
            logger.error(f"Error obteniendo los trabajadores de oferta {oferta.id}: {str(e)}")
            raise

    @staticmethod
    def getOfertasDisponibles(calendario):
        try:
            return Oferta.getOfertasDisponibles(calendario)
        except Exception as e:
            logger.error(f"Error obteniendo las ofertas disponibles: {str(e)}")
            raise
