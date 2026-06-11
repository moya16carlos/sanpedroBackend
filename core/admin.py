from django.contrib import admin

from .models import (
    Cargos,
    CategoriasNotificacion,
    Clientes,
    Comunas,
    Membresias,
    Organizaciones,
    Personas,
    PreferenciasNotificacion,
    Provincias,
    Regiones,
    Reportes,
    Sectores,
    TiposNotificacion,
    HistorialReportes,
    AuditoriaAdmin,
    DispositivosUsuario,
    NotificacionesEnviadas,
)


@admin.register(Personas)
class PersonasAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'rut',
        'email',
        'telefono',
        'metodo_auth',
        'comuna_id',
        'sector_id',
    )

    search_fields = (
        'nombre',
        'rut',
        'email',
        'telefono',
        'auth_id',
    )

    list_filter = (
        'metodo_auth',
        'comuna_id',
        'sector_id',
    )

    ordering = ('id',)

@admin.register(Reportes)
class ReportesAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'titulo', 'tipo', 'autor',
        'estado_validacion', 'estado_municipio',
        'fecha_creacion', 'es_visitante',
    )
    search_fields = ('titulo', 'descripcion', 'tipo', 'autor__nombre', 'autor__rut')
    list_filter = ('tipo', 'estado_validacion', 'estado_municipio', 'es_visitante')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion', 'fecha_validacion')


@admin.register(Sectores)
class SectoresAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'comuna')
    search_fields = ('nombre', 'comuna__nombre')
    list_filter = ('comuna',)
    ordering = ('nombre',)


@admin.register(Organizaciones)
class OrganizacionesAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'tipo', 'rut', 'sector_id')
    search_fields = ('nombre', 'rut', 'tipo')
    list_filter = ('tipo', 'sector_id')
    ordering = ('nombre',)


@admin.register(Membresias)
class MembresiasAdmin(admin.ModelAdmin):
    list_display = ('id', 'persona', 'organizacion', 'cargo_id', 'fecha_ingreso')
    search_fields = ('persona__nombre', 'persona__rut', 'organizacion__nombre')
    list_filter = ('organizacion', 'cargo_id')
    ordering = ('-fecha_ingreso',)
    readonly_fields = ('fecha_ingreso',)


@admin.register(Comunas)
class ComunasAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'provincia', 'contrato_activo', 'slug')
    search_fields = ('nombre', 'slug', 'provincia__nombre')
    list_filter = ('contrato_activo', 'provincia')
    ordering = ('nombre',)


@admin.register(Provincias)
class ProvinciasAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'region')
    search_fields = ('nombre', 'region__nombre')
    list_filter = ('region',)
    ordering = ('nombre',)


@admin.register(Regiones)
class RegionesAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'numero_region')
    search_fields = ('nombre', 'numero_region')
    ordering = ('nombre',)


@admin.register(Cargos)
class CargosAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'nombre', 'rut', 'tipo_cliente',
        'comuna', 'sector_id',
        'estado_contrato', 'plan_suscripcion',
        'fecha_inicio_contrato', 'fecha_fin_contrato',
    )
    search_fields = ('nombre', 'rut', 'contacto_email', 'contacto_nombre')
    list_filter = ('tipo_cliente', 'estado_contrato', 'comuna', 'sector_id')
    ordering = ('nombre',)
    readonly_fields = ('creado_en', 'actualizado_en')


@admin.register(CategoriasNotificacion)
class CategoriasNotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(TiposNotificacion)
class TiposNotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'descripcion')
    search_fields = ('nombre', 'descripcion', 'categoria__nombre')
    list_filter = ('categoria',)
    ordering = ('nombre',)


@admin.register(PreferenciasNotificacion)
class PreferenciasNotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'persona', 'tipo_notificacion_id', 'activo')
    search_fields = ('persona__nombre', 'persona__rut')
    list_filter = ('activo', 'tipo_notificacion_id')


@admin.register(HistorialReportes)
class HistorialReportesAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporte_id', 'accion', 'detalle', 'fecha')
    search_fields = ('accion', 'detalle')
    list_filter = ('accion',)
    ordering = ('-fecha',)
    readonly_fields = ('fecha',)


@admin.register(AuditoriaAdmin)
class AuditoriaAdminAdmin(admin.ModelAdmin):
    list_display = ('id', 'accion', 'modulo', 'usuario_sistema', 'ip', 'fecha')
    search_fields = ('accion', 'modulo', 'detalle', 'usuario_sistema', 'ip')
    list_filter = ('accion', 'modulo', 'usuario_sistema')
    ordering = ('-fecha',)
    readonly_fields = ('fecha',)


@admin.register(DispositivosUsuario)
class DispositivosUsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'persona_id', 'plataforma',
        'activo', 'fecha_registro', 'ultimo_acceso',
    )
    search_fields = ('fcm_token', 'plataforma')
    list_filter = ('plataforma', 'activo')
    ordering = ('-ultimo_acceso',)
    readonly_fields = ('fecha_registro', 'ultimo_acceso')


@admin.register(NotificacionesEnviadas)
class NotificacionesEnviadasAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'destinatario', 'sector_id', 'organizacion_id',
        'titulo', 'total_destinatarios',
        'enviados', 'errores', 'fecha',
    )
    search_fields = ('titulo', 'mensaje', 'destinatario')
    list_filter = ('destinatario', 'sector_id', 'organizacion_id')
    ordering = ('-fecha',)
    readonly_fields = ('fecha',)


from .models import AccesoFuncionario

@admin.register(AccesoFuncionario)
class AccesoFuncionarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'nombre', 'rol', 'activo', 'creado_en')
    search_fields = ('email', 'nombre')
    list_filter = ('rol', 'activo')