from rest_framework import serializers
from ..base.models.usuario import Jornalero, Propietario
from ..base.models.periodo import Periodo
from ..base.models.calendario import Calendario

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
