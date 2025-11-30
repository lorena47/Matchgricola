
import logging
from django.core.exceptions import ValidationError
from ..models.usuario import Jornalero, Propietario
from ..models.suscripcion import Suscripcion

logger = logging.getLogger('servicio')

class SuscripcionService:
    
    @staticmethod
    def getOfertasDisponibles(jornalero):
        try:
            jornalero.getOfertasDisponibles()
        except Exception as e:
            logger.error(f"Error obteniendo las ofertas disponibles para el jornalero {jornalero.usuario}: {str(e)}")
            raise

    @staticmethod
    def getJornalerosDisponibles(propietario):
        try:
            propietario.getJornalerosDisponibles()
        except Exception as e:
            logger.error(f"Error obteniendo los jornaleros disponibles para el propietario {propietario.usuario}: {str(e)}")
            raise

    @staticmethod
    def suscribir(jornalero, oferta):
        return jornalero.suscribir(oferta)
    
    @staticmethod
    def proponer(propietario, oferta, jornalero):
        return propietario.proponer(oferta, jornalero)

    @staticmethod
    def aceptarSuscripcion(propietario, suscripcion):
        try:
            propietario.aceptarSuscripcion(suscripcion)
        except ValidationError as e:
            logger.warning(f"No se pudo aceptar la suscripcion: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error aceptando la suscripcion: {str(e)}")
            raise
        
    @staticmethod
    def aceptarPropuesta(jornalero, propuesta):
        try:
            jornalero.aceptarSuscripcion(propuesta)
        except ValidationError as e:
            logger.warning(f"No se pudo aceptar la propuesta: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error aceptando la propuesta: {str(e)}")
            raise
    
    @staticmethod
    def aceptarPropuesta(jornalero, propuesta):
        try:
            jornalero.aceptarSuscripcion(propuesta)
        except ValidationError as e:
            logger.warning(f"No se pudo aceptar la propuesta: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error aceptando la propuesta: {str(e)}")
            raise

    @staticmethod
    def cancelarSuscripcion(usuario, suscripcion):
        try:
            usuario.cancelarSuscripcion(suscripcion)  
        except ValidationError as e:
            logger.warning(f"No se pudo cancelar la suscripción: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error cancelando la suscripción: {str(e)}")
            raise
        
    @staticmethod
    def getTrabajos(usuario):
        try:
            return usuario.getTrabajos()
        except Exception as e:
            logger.error(f"Error obteniendo los trabajos de {usuario.usuario}: {str(e)}")
            raise
