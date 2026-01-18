from rest_framework import serializers
from ..base.models.usuario import Jornalero, Propietario
from ..base.models.periodo import Periodo
from ..base.models.calendario import Calendario
from ..base.models.oferta import Oferta
from ..base.models.suscripcion import Suscripcion

class JornaleroSerializer(serializers.ModelSerializer):
    contrasenia = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = Jornalero
        fields = ['usuario', 'nombre', 'correo', 'contrasenia', 'telefono']

class PropietarioSerializer(serializers.ModelSerializer):
    contrasenia = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = Propietario
        fields = ['usuario', 'nombre', 'correo', 'contrasenia', 'telefono']

class PeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = ["id", "fecha_inicio", "fecha_fin"]
    
    def validate(self, data):
        if data['fecha_inicio'] > data['fecha_fin']:
            raise serializers.ValidationError({
                'fecha_inicio': 'La fecha de inicio no puede ser posterior a la fecha de fin.'
            })
        return data
    
class FechasSerializer(serializers.Serializer):
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()

class CalendarioSerializer(serializers.ModelSerializer):
    jornalero = serializers.PrimaryKeyRelatedField(queryset=Jornalero.objects.all())
    periodos = PeriodoSerializer(many=True, read_only=True)

    class Meta:
        model = Calendario
        fields = ["id", "jornalero", "periodos"]

class OfertaSerializer(serializers.ModelSerializer):
    propietario = serializers.PrimaryKeyRelatedField(
        queryset=Propietario.objects.all()
    )
    periodo = serializers.PrimaryKeyRelatedField(
        queryset=Periodo.objects.all()
    )

    class Meta:
        model = Oferta
        fields = [
            "id",
            "titulo",
            "descripcion",
            "plazas",
            "euros_hora",
            "periodo",
            "propietario",
        ]

class SuscripcionSerializer(serializers.ModelSerializer):
    jornalero = serializers.SlugRelatedField(
        slug_field="usuario",
        queryset=Jornalero.objects.all()
    )

    oferta = serializers.PrimaryKeyRelatedField(
        queryset=Oferta.objects.all()
    )

    class Meta:
        model = Suscripcion
        fields = [
            "id",
            "jornalero",
            "oferta",
            "trabajo",
            "activa",
            "interesado",
        ]


class PeriodoFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = ["fecha_inicio", "fecha_fin"]

class OfertaFeedSerializer(serializers.ModelSerializer):
    propietario = serializers.StringRelatedField()
    periodo = serializers.StringRelatedField()

    class Meta:
        model = Oferta
        fields = [
            "id",
            "titulo",
            "descripcion",
            "plazas",
            "euros_hora",
            "periodo",
            "propietario",
        ]

class JornaleroFeedSerializer(serializers.Serializer):
    usuario = serializers.CharField()
    calendario_id = serializers.IntegerField()
    periodos_disponibles = PeriodoFeedSerializer(many=True)
    ofertas_disponibles = OfertaFeedSerializer(many=True)

class SuscripcionFeedSerializer(serializers.ModelSerializer):
    jornalero = serializers.StringRelatedField()
    oferta = serializers.StringRelatedField()

    class Meta:
        model = Suscripcion
        fields = ["id", "jornalero", "oferta", "trabajo"]


class PropietarioFeedSerializer(serializers.Serializer):
    usuario = serializers.CharField()
    ofertas = OfertaSerializer(many=True)
    pendientes = SuscripcionFeedSerializer(many=True)
    aceptadas = SuscripcionFeedSerializer(many=True)
    



