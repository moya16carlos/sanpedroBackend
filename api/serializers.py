from rest_framework import serializers
from core.models import (
    Comunas, Sectores, Cargos, Organizaciones,
    Personas, Membresias, Reportes
)


class ComunasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunas
        fields = '__all__'


class SectoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sectores
        fields = '__all__'


class CargosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargos
        fields = '__all__'


class OrganizacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizaciones
        fields = '__all__'


class PersonasSerializer(serializers.ModelSerializer):
    es_dirigente = serializers.BooleanField(write_only=True, required=False, default=False)
    organizacion_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    cargo_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Personas
        fields = [
            'id', 'metodo_auth', 'auth_id', 'identidad_validada',
            'fecha_registro', 'ultimo_acceso',
            'nombre', 'rut', 'genero', 'telefono', 'email',
            'comuna_id', 'sector_id',
            'es_dirigente', 'organizacion_id', 'cargo_id'
        ]

    def create(self, validated_data):
        es_dirigente = validated_data.pop('es_dirigente', False)
        organizacion_id = validated_data.pop('organizacion_id', None)
        cargo_id = validated_data.pop('cargo_id', None)

        persona = Personas.objects.create(**validated_data)

        if es_dirigente and organizacion_id and cargo_id:
            Membresias.objects.create(
                persona=persona,
                organizacion_id=organizacion_id,
                cargo_id=cargo_id
            )

        return persona


class ReportesSerializer(serializers.ModelSerializer):
    autor_nombre = serializers.CharField(source='autor.nombre', read_only=True)

    class Meta:
        model = Reportes
        fields = [
            'id',
            'autor',
            'autor_nombre',
            'validador',
            'tipo',
            'titulo',
            'descripcion',
            'latitud',
            'longitud',
            'foto_url',
            'estado_validacion',
            'estado_municipio',
            'fecha_creacion',
            'fecha_validacion',
            'es_visitante',
        ]
        read_only_fields = [
            'fecha_creacion',
            'fecha_validacion',
            'autor_nombre',
        ]