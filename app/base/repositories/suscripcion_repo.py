import logging
from django.core.exceptions import ValidationError
from ..models.suscripcion import Suscripcion

logger = logging.getLogger('suscripcion')

class SuscripcionRepository:

    @staticmethod
    def crear(jornalero, oferta, usuario_interesado):
        try:
            suscripcion = Suscripcion.crear(jornalero, oferta, usuario_interesado)
            logger.info(f"Suscripcion creada: jornalero={jornalero.usuario}, oferta={oferta.id}, interesado={usuario_interesado}")
            return suscripcion
        except ValidationError as e:
            logger.warning(f"No se pudo crear la suscripcion: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creando la suscripcion: {str(e)}")
            raise

    @staticmethod
    def existe(id):
        try:
            return Suscripcion.existe(id)
        except Exception as e:
            logger.error(f"Error verificando existencia de suscripcion {id}: {str(e)}")
            raise

    @staticmethod
    def getMatchsOferta(oferta):
        try:
            return Suscripcion.getMatchsOferta(oferta)
        except Exception as e:
            logger.error(f"Error obteniendo matches de la oferta {oferta.id}: {str(e)}")
            raise

    @staticmethod
    def getMatchsJornalero(jornalero):
        try:
            return Suscripcion.getMatchsJornalero(jornalero)
        except Exception as e:
            logger.error(f"Error obteniendo matches del jornalero {jornalero.usuario}: {str(e)}")
            raise

    @staticmethod
    def getLikesJornalero(jornalero):
        try:
            return Suscripcion.getLikesJornalero(jornalero)
        except Exception as e:
            logger.error(f"Error obteniendo likes para jornalero {jornalero.usuario}: {str(e)}")
            raise
        
    @staticmethod
    def getSuscripcionesActivas(usuario):
        try:
            return Suscripcion.getSuscripcionesActivas(usuario)
        except Exception as e:
            logger.error(f"Error obteniendo suscripciones activas para {usuario.usuario}: {str(e)}")
            raise
