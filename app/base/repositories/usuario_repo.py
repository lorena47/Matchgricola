import logging
from django.core.exceptions import ValidationError
from ..models.usuario import Usuario, Propietario, Jornalero

logger = logging.getLogger('usuario')

class UsuarioRepository:

    @staticmethod
    def crearUsuario(usuario, nombre, correo, contrasenia, telefono=None):
        try:
            cuenta = Usuario.crear(usuario, nombre, correo, contrasenia, telefono)
            logger.info(f"Usuario {usuario} creado")
            return cuenta
        except ValidationError as e:
            logger.warning(f"No se pudo crear usuario {usuario}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creando usuario {usuario}: {str(e)}")
            raise

    @staticmethod
    def existe(usuario):
        try:
            return Usuario.existe(usuario)
        except Exception as e:
            logger.error(f"Error verificando existencia de usuario {usuario}: {str(e)}")
            raise

    @staticmethod
    def borrar(usuario):
        try:
            usuario.borrar()
            logger.info(f"Usuario {usuario.usuario} borrado")
        except Exception as e:
            logger.error(f"Error borrando usuario {usuario.usuario}: {str(e)}")
            raise

    @staticmethod
    def identificar(usuario, contrasenia):
        try:
            return usuario.identificar(contrasenia)
        except Exception as e:
            logger.error(f"Error identificando usuario {usuario.usuario}: {str(e)}")
            raise

    ###################################################
    # ------------------ Propietario ------------------
    ###################################################

    @staticmethod
    def crearPropietario(usuario, nombre, correo, contrasenia, telefono=None):
        try:
            propietario = Propietario.crear(usuario, nombre, correo, contrasenia, telefono)
            logger.info(f"Propietario {usuario} creado")
            return propietario
        except ValidationError as e:
            logger.warning(f"No se pudo crear propietario {usuario}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creando propietario {usuario}: {str(e)}")
            raise

    @staticmethod
    def getOfertas(propietario):
        try:
            return propietario.getOfertas()
        except Exception as e:
            logger.error(f"Error obteniendo las ofertas del propietario {propietario.usuario}: {str(e)}")
            raise

    @staticmethod
    def getOferta(propietario, indice):
        try:
            return propietario.getOferta(indice)
        except IndexError as e:
            logger.warning(f"Índice fuera de rango para el propietario {propietario.usuario}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error obteniendo oferta para el propietario {propietario.usuario}: {str(e)}")
            raise

    #################################################
    # ------------------ Jornalero ------------------
    #################################################

    @staticmethod
    def crearJornalero(usuario, nombre, correo, contrasenia, telefono=None):
        try:
            jornalero = Jornalero.crear(usuario, nombre, correo, contrasenia, telefono)
            logger.info(f"Jornalero {usuario} creado")

            try:
              jornalero.tenerCalendario()
              logger.info(f"Calendario creado para el jornalero {jornalero.usuario}")
            except Exception as e:
              logger.error(f"Error creando un calendario para el jornalero {jornalero.usuario}: {str(e)}")
              raise
            
            return jornalero
        except ValidationError as e:
            logger.warning(f"No se pudo crear jornalero {usuario}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creando jornalero {usuario}: {str(e)}")
            raise

    @staticmethod
    def getCalendario(jornalero):
        try:
            return jornalero.getCalendario()
        except Exception as e:
            logger.error(f"Error obteniendo el calendario del jornalero {jornalero.usuario}: {str(e)}")
            raise
