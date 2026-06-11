# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Cargos(models.Model):
    nombre = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'cargos'


class CategoriasNotificacion(models.Model):
    nombre = models.CharField(unique=True, max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categorias_notificacion'


class Clientes(models.Model):
    tipo_cliente = models.TextField()  # This field type is a guess.
    nombre = models.CharField(max_length=200)
    rut = models.CharField(unique=True, max_length=20, blank=True, null=True)
    comuna = models.ForeignKey('Comunas', models.DO_NOTHING, blank=True, null=True)
    sector_id = models.IntegerField(blank=True, null=True)
    estado_contrato = models.TextField(blank=True, null=True)  # This field type is a guess.
    plan_suscripcion = models.CharField(max_length=100, blank=True, null=True)
    fecha_inicio_contrato = models.DateField(blank=True, null=True)
    fecha_fin_contrato = models.DateField(blank=True, null=True)
    contacto_nombre = models.CharField(max_length=150, blank=True, null=True)
    contacto_email = models.CharField(max_length=150, blank=True, null=True)
    contacto_telefono = models.CharField(max_length=50, blank=True, null=True)
    creado_en = models.DateTimeField(blank=True, null=True)
    actualizado_en = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clientes'


class Comunas(models.Model):
    provincia = models.ForeignKey('Provincias', models.DO_NOTHING)
    nombre = models.CharField(max_length=100)
    contrato_activo = models.BooleanField(blank=True, null=True)
    slug = models.CharField(unique=True, max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comunas'


class Membresias(models.Model):
    persona = models.ForeignKey('Personas', models.DO_NOTHING)
    organizacion = models.ForeignKey('Organizaciones', models.DO_NOTHING)
    cargo_id = models.IntegerField(blank=True, null=True)
    fecha_ingreso = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'membresias'
        unique_together = (('persona', 'organizacion'),)


class Organizaciones(models.Model):
    sector_id = models.IntegerField()
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    rut = models.CharField(unique=True, max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'organizaciones'


class Personas(models.Model):
    metodo_auth = models.CharField(max_length=50, blank=True, null=True)
    auth_id = models.CharField(max_length=255, blank=True, null=True)
    nombre = models.CharField(max_length=200)
    rut = models.CharField(max_length=20, blank=True, null=True)
    genero = models.CharField(max_length=50, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    comuna_id = models.IntegerField(blank=True, null=True)
    sector_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'personas'
        
class PreferenciasNotificacion(models.Model):
    persona = models.ForeignKey(Personas, models.DO_NOTHING)
    tipo_notificacion_id = models.IntegerField()
    activo = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'preferencias_notificacion'
        unique_together = (('persona', 'tipo_notificacion_id'),)


class Provincias(models.Model):
    region = models.ForeignKey('Regiones', models.DO_NOTHING)
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'provincias'


class Regiones(models.Model):
    nombre = models.CharField(unique=True, max_length=100)
    numero_region = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'regiones'


class Reportes(models.Model):
    autor = models.ForeignKey(
        Personas,
        models.DO_NOTHING,
        db_column='autor_id',
        blank=True,
        null=True
    )
    validador = models.ForeignKey(
        Personas,
        models.DO_NOTHING,
        db_column='validador_id',
        related_name='reportes_validador_set',
        blank=True,
        null=True
    )
    cliente_id = models.IntegerField(blank=True, null=True)
    categoria_id = models.IntegerField(blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    latitud = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    foto_url = models.CharField(max_length=500, blank=True, null=True)
    video_url = models.CharField(max_length=500, blank=True, null=True)
    estado_validacion = models.CharField(max_length=50, blank=True, null=True)
    estado_municipio = models.CharField(max_length=50, blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_validacion = models.DateTimeField(blank=True, null=True)
    es_visitante = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reportes'

class Sectores(models.Model):
    comuna = models.ForeignKey(Comunas, models.DO_NOTHING)
    nombre = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'sectores'


class TiposNotificacion(models.Model):
    categoria = models.ForeignKey(CategoriasNotificacion, models.DO_NOTHING)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipos_notificacion'

class HistorialReportes(models.Model):
    id = models.AutoField(primary_key=True)
    reporte_id = models.IntegerField()
    accion = models.CharField(max_length=100, blank=True, null=True)
    detalle = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'historial_reportes'


class AuditoriaAdmin(models.Model):
    id = models.AutoField(primary_key=True)
    accion = models.CharField(max_length=100, blank=True, null=True)
    modulo = models.CharField(max_length=100, blank=True, null=True)
    detalle = models.TextField(blank=True, null=True)
    usuario_sistema = models.CharField(max_length=150, blank=True, null=True)
    ip = models.CharField(max_length=100, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auditoria_admin'

class DispositivosUsuario(models.Model):
    id = models.AutoField(primary_key=True)
    persona_id = models.IntegerField()
    fcm_token = models.TextField(unique=True)
    plataforma = models.CharField(max_length=50, blank=True, null=True)
    activo = models.BooleanField(blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    ultimo_acceso = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dispositivos_usuario'


class NotificacionesEnviadas(models.Model):
    id = models.AutoField(primary_key=True)
    destinatario = models.CharField(max_length=50, blank=True, null=True)
    sector_id = models.IntegerField(blank=True, null=True)
    organizacion_id = models.IntegerField(blank=True, null=True)
    titulo = models.CharField(max_length=200, blank=True, null=True)
    mensaje = models.TextField(blank=True, null=True)
    total_destinatarios = models.IntegerField(blank=True, null=True)
    enviados = models.IntegerField(blank=True, null=True)
    errores = models.IntegerField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notificaciones_enviadas'


#### LISTA BLANCA CORREOS ###
class AccesoFuncionario(models.Model):
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=200, blank=True, null=True)
    rol = models.CharField(max_length=50, default='FUNCIONARIO')
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accesos_funcionarios'

    def __str__(self):
        return self.email