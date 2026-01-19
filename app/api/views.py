from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from ..base.models.usuario import Jornalero, Propietario
from ..base.models.periodo import Periodo
from ..base.models.calendario import Calendario
from ..base.models.oferta import Oferta
from ..base.models.suscripcion import Suscripcion
from .serializers import JornaleroSerializer, PropietarioSerializer, PeriodoSerializer, CalendarioSerializer, FechasSerializer, OfertaSerializer, SuscripcionSerializer, JornaleroFeedSerializer, PropietarioFeedSerializer, SuscripcionFeedSerializer

from ..base.repositories.usuario_repo import UsuarioRepository
from ..base.repositories.periodo_repo import PeriodoRepository 
from ..base.repositories.calendario_repo import CalendarioRepository
from ..base.repositories.oferta_repo import OfertaRepository
from ..base.repositories.suscripcion_repo import SuscripcionRepository

from ..base.services.suscripcion_serv import SuscripcionService
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import login
from django.contrib.auth.models import User


import logging

import sentry_sdk
from time import time


logger = logging.getLogger('vista')

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        usuario_txt = request.data.get("usuario")
        contrasenia = request.data.get("contrasenia")

        logger.info("Intento de login recibido")

        if not usuario_txt or not contrasenia:
            logger.warning("Login fallido: faltan credenciales")
            return Response(
                {"error": "Usuario y contraseña requeridos"},
                status=400
            )

        try:
            try:
                usuario = Jornalero.objects.get(usuario=usuario_txt)
                tipo = "jornalero"
            except Jornalero.DoesNotExist:
                usuario = Propietario.objects.get(usuario=usuario_txt)
                tipo = "propietario"

            logger.info(f"Usuario {usuario_txt} encontrado como {tipo}")

        except Propietario.DoesNotExist:
            logger.warning(f"Login fallido: usuario {usuario_txt} no encontrado")
            return Response(
                {"error": "Usuario no encontrado"},
                status=404
            )
        except Exception as e:
            logger.error(
                f"Error buscando usuario {usuario_txt}: {str(e)}",
                exc_info=True
            )
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "Error interno del servidor"},
                status=500
            )

        try:
            UsuarioRepository.identificar(usuario, contrasenia)
            logger.info(f"Login correcto para usuario {usuario_txt}")

        except Exception:
            logger.warning(f"Login fallido: contraseña incorrecta para {usuario_txt}")
            return Response(
                {"error": "Credenciales incorrectas"},
                status=401
            )
        
        user = User.objects.get(username=usuario.usuario)
        login(request, user)

        return Response({
            "usuario": usuario.usuario,
            "tipo": tipo
        })


class JornaleroViewSet(viewsets.ModelViewSet):
    queryset = Jornalero.objects.all()
    serializer_class = JornaleroSerializer

    def perform_create(self, serializer):
        data = serializer.validated_data

        with sentry_sdk.start_transaction(
            op="jornalero.create",
            name="Crear Jornalero"
        ) as transaction:

            inicio = time()
            try:
                logger.info(f"Creando jornalero {data.get('usuario')}")

                jornalero = UsuarioRepository.crearJornalero(
                    usuario=data.get('usuario'),
                    nombre=data.get('nombre'),
                    correo=data.get('correo'),
                    contrasenia=data.get('contrasenia'),
                    telefono=data.get('telefono')
                )

                serializer.instance = jornalero
                duracion = time() - inicio

                transaction.set_tag("jornalero.usuario", data.get("usuario"))
                transaction.set_measurement("duration", duracion)

                logger.info(f"Jornalero {jornalero.usuario} creado correctamente")

            except Exception as e:
                sentry_sdk.set_context("jornalero", {
                    "usuario": data.get("usuario"),
                    "correo": data.get("correo"),
                })
                sentry_sdk.capture_exception(e)
                logger.error(f"Error creando jornalero: {str(e)}")
                raise

    def perform_destroy(self, instance):
        try:
            logger.info(f"Borrando jornalero {instance.usuario}")
            UsuarioRepository.borrar(instance)
        except Exception as e:
            logger.error(f"Error borrando jornalero: {str(e)}")
            raise

    @action(detail=True, methods=["get"])
    def calendario(self, request, pk=None):
        jornalero = self.get_object()
        try:
            calendario = UsuarioRepository.getCalendario(jornalero)
            return Response(calendario)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
    
    @action(detail=True, methods=["get"])
    def feed(self, request, pk=None):
        logger.info(f"Solicitud de feed para jornalero {pk}")

        try:
            jornalero = self.get_object()
            logger.info(f"Jornalero {jornalero.usuario} encontrado")

            calendario = jornalero.getCalendario()
            periodos = calendario.periodos.all()
            logger.info(f"Calendario con {periodos.count()} periodos")

            ofertas = jornalero.getOfertasDisponibles()
            logger.info(f"{len(ofertas)} ofertas disponibles")

            data = {
                "usuario": jornalero.usuario,
                "calendario_id": calendario.id,
                "periodos_disponibles": periodos,
                "ofertas_disponibles": ofertas,
            }

            serializer = JornaleroFeedSerializer(data)
            return Response(serializer.data)

        except Exception as e:
            logger.error(
                f"Error obteniendo feed del jornalero {pk}: {str(e)}",
                exc_info=True
            )
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "No se pudo obtener el feed del jornalero"},
                status=500
            )


class PropietarioViewSet(viewsets.ModelViewSet):
    queryset = Propietario.objects.all()
    serializer_class = PropietarioSerializer

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            logger.info(f"Creando propietario {data.get('usuario')}")
            propietario = UsuarioRepository.crearPropietario(
                usuario=data.get('usuario'),
                nombre=data.get('nombre'),
                correo=data.get('correo'),
                contrasenia=data.get('contrasenia'),
                telefono=data.get('telefono')
            )
            serializer.instance = propietario
            logger.info(f"Propietario {propietario.usuario} creado correctamente")
        except Exception as e:
            logger.error(f"Error creando jornalero: {str(e)}")
            raise

    def perform_destroy(self, instance):
        try:
            logger.info(f"Borrando propietario {instance.usuario}")
            UsuarioRepository.borrar(instance)
        except Exception as e:
            logger.error(f"Error borrando propietario: {str(e)}")
            raise

    @action(detail=True, methods=["get"])
    def ofertas(self, request, pk=None):
        propietario = self.get_object()
        try:
            ofertas = UsuarioRepository.getOfertas(propietario)
            serializer = OfertaSerializer(ofertas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=True, methods=["get"])
    def oferta(self, request, pk=None):
        propietario = self.get_object()
        indice = int(request.query_params.get("indice", 0))
        try:
            oferta = UsuarioRepository.getOferta(propietario, indice)
            serializer = OfertaSerializer(oferta)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        
    @action(detail=True, methods=["get"])
    def feed(self, request, pk=None):
        propietario = self.get_object()

        ofertas = propietario.getOfertas()
        jornaleros_disponibles = propietario.getJornalerosDisponibles()

        mis_propuestas = []
        suscripciones_recibidas = []
        aceptadas = []

        for oferta in ofertas:
            for s in oferta.suscripciones.all():
                if s.trabajo:
                    aceptadas.append(s)
                elif s.activa:
                    if s.interesado == "propietario":
                        mis_propuestas.append(s)
                    else:
                        suscripciones_recibidas.append(s)


        data = {
            "ofertas": OfertaSerializer(ofertas, many=True).data,
            "jornaleros_disponibles": {
                oferta.id: JornaleroSerializer(jornaleros, many=True).data
                for oferta, jornaleros in jornaleros_disponibles.items()
            },
            "mis_propuestas": SuscripcionSerializer(mis_propuestas, many=True).data,
            "suscripciones": SuscripcionSerializer(suscripciones_recibidas, many=True).data,
            "aceptadas": SuscripcionSerializer(aceptadas, many=True).data,
        }


        return Response(data)
        
        
class PeriodoViewSet(viewsets.ModelViewSet):
    queryset = Periodo.objects.all()
    serializer_class = PeriodoSerializer

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            periodo = PeriodoRepository.crear(
                fecha_inicio=data.get('fecha_inicio'),
                fecha_fin=data.get('fecha_fin')
            )
            serializer.instance = periodo
        except Exception as e:
            logger.error(f"Error creando periodo: {str(e)}")
            raise

    def perform_destroy(self, instance):
        try:
            logger.info(f"Borrando periodo {instance.id}")
            PeriodoRepository.borrar(instance)
        except ValidationError as e:
            logger.warning(f"No se puede borrar periodo {instance.id}: {str(e)}")
            raise DRFValidationError({"warning": str(e)})
        except Exception as e:
            logger.error(f"Error borrando periodo {instance.id}: {str(e)}")
            raise

class CalendarioViewSet(viewsets.ModelViewSet):
    queryset = Calendario.objects.all()
    serializer_class = CalendarioSerializer

    def perform_create(self, serializer):
        jornalero = serializer.validated_data.get('jornalero')
        try:
            calendario = CalendarioRepository.crear(jornalero)
            serializer.instance = calendario
        except Exception as e:
            logger.error(f"Error creando calendario: {str(e)}")
            raise

    def perform_destroy(self, instance):
        try:
            CalendarioRepository.borrar(instance)
        except Exception as e:
            logger.error(f"Error borrando calendario {instance.id}: {str(e)}")
            raise

    @action(detail=True, methods=["post"], serializer_class=FechasSerializer)
    def incluir_periodo(self, request, pk=None):
        calendario = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inicio = serializer.validated_data['fecha_inicio']
        fin = serializer.validated_data['fecha_fin']

        try:
            CalendarioRepository.incluirPeriodo(calendario, inicio, fin)
            return Response({"info": f"Periodo {inicio} → {fin} incluido"})
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=True, methods=["post"], serializer_class=FechasSerializer)
    def quitar_periodo(self, request, pk=None):
        calendario = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inicio = serializer.validated_data['fecha_inicio']
        fin = serializer.validated_data['fecha_fin']

        try:
            CalendarioRepository.quitarPeriodo(calendario, inicio, fin)
            return Response({"info": f"Periodo {inicio} → {fin} excluido"})
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class OfertaViewSet(viewsets.ModelViewSet):
    queryset = Oferta.objects.all()
    serializer_class = OfertaSerializer

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            oferta = OfertaRepository.crear(
                titulo=data["titulo"],
                descripcion=data["descripcion"],
                plazas=data["plazas"],
                eurosHora=data["euros_hora"],
                fechaInicio=data["periodo"].fecha_inicio,
                fechaFin=data["periodo"].fecha_fin,
                propietario=data["propietario"],
            )
            serializer.instance = oferta
        except Exception as e:
            logger.error(f"Error creando oferta: {str(e)}")
            raise

    def perform_destroy(self, instance):
        try:
            OfertaRepository.borrar(instance)
        except Exception as e:
            logger.error(f"Error borrando oferta {instance.id}: {str(e)}")
            raise

class SuscripcionViewSet(viewsets.ModelViewSet):
    serializer_class = SuscripcionSerializer

    def get_queryset(self):
        qs = Suscripcion.objects.all()

        if self.request.query_params.get("jornalero"):
            jornalero = self.request.query_params.get("jornalero")
            return qs.filter(jornalero__usuario=jornalero)

        if self.request.query_params.get("propietario"):
            propietario = self.request.query_params.get("propietario")
            return qs.filter(oferta__propietario__usuario=propietario)

        return qs

    def perform_create(self, serializer):

        data = serializer.validated_data
        interesado = data["interesado"]

        if isinstance(interesado, list):
            interesado = interesado[0]

        if isinstance(interesado, str):
            interesado = (
                interesado
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
                .replace('"', "")
                .strip()
                .lower()
            )

        logger.info(f"Interesado: {interesado}")

        try:
            suscripcion = SuscripcionRepository.crear(
                jornalero=data["jornalero"],
                oferta=data["oferta"],
                usuario_interesado=interesado,
            )
            serializer.instance = suscripcion

        except ValidationError as e:
            logger.error(f"Error creando suscripcion: {e}")
            raise


    @action(detail=True, methods=["post"])
    def aceptar(self, request, pk=None):
        suscripcion = self.get_object()

        try:
            suscripcion.trabajar()
            return Response(
                {"info": "Suscripción aceptada"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    @action(detail=True, methods=["post"])
    def rechazar(self, request, pk=None):
        suscripcion = self.get_object()
        username = request.user.username

        if username == suscripcion.jornalero.usuario:
            rol = "jornalero"
        elif username == suscripcion.oferta.propietario.usuario:
            rol = "propietario"
        else:
            return Response(
                {"error": "No autorizado para rechazar esta suscripción"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            suscripcion.rechazar(rol)
            return Response(
                {"info": "Suscripción rechazada"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

