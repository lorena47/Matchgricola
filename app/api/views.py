from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from ..base.models.usuario import Jornalero, Propietario
from ..base.models.periodo import Periodo
from ..base.models.calendario import Calendario
from .serializers import JornaleroSerializer, PropietarioSerializer, PeriodoSerializer, CalendarioSerializer, FechasSerializer
from ..base.repositories.usuario_repo import UsuarioRepository
from ..base.repositories.periodo_repo import PeriodoRepository 
from ..base.repositories.calendario_repo import CalendarioRepository
import logging

import sentry_sdk
from time import time


logger = logging.getLogger('vista')

class JornaleroViewSet(viewsets.ModelViewSet):
    queryset = Jornalero.objects.all()
    serializer_class = JornaleroSerializer

    def perform_create(self, serializer):
        data = serializer.validated_data
        with sentry_sdk.start_transaction(
            op="jornalero.create",
            name="Crear Jornalero"
        ):
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
                sentry_sdk.metrics.timing("jornalero.create.time", duracion, unit="second")
                sentry_sdk.metrics.incr("jornalero.create.count")

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
            return Response(ofertas)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=True, methods=["get"])
    def oferta(self, request, pk=None):
        propietario = self.get_object()
        indice = int(request.query_params.get("indice", 0))
        try:
            oferta = UsuarioRepository.getOferta(propietario, indice)
            return Response(oferta)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        
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