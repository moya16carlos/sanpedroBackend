from django.urls import path


from .views import (
    ComunasListView,
    SectoresListView,
    CargosListView,
    OrganizacionesListView,
    RegistroPersonaView,
    PerfilPersonaView,
    ReportesListCreateView,
    LoginGoogleView,
    PerfilActualView,
    MisReportesView,
    DashboardUsuarioView,
    ReporteDetalleView,
    ReporteFotoUrlView,
    S3PresignedUrlView,
    ActualizarEstadoReporteView,
    DashboardMunicipalView,
    RegistrarDispositivoView,
)

urlpatterns = [
    path('comunas/', ComunasListView.as_view(), name='api_comunas'),
    path('sectores/', SectoresListView.as_view(), name='api_sectores'),
    path('cargos/', CargosListView.as_view(), name='api_cargos'),
    path('organizaciones/', OrganizacionesListView.as_view(), name='api_organizaciones'),

    path('registro/', RegistroPersonaView.as_view(), name='api_registro'),
    path('perfil/', PerfilPersonaView.as_view(), name='api_perfil'),

    path('reportes/', ReportesListCreateView.as_view(), name='api_reportes'),
    path('login-google/', LoginGoogleView.as_view(), name='api_login_google'),
    path('perfil-actual/', PerfilActualView.as_view(), name='api_perfil_actual'),
    path('mis-reportes/', MisReportesView.as_view(), name='api_mis_reportes'),
    path('dashboard/', DashboardUsuarioView.as_view(), name='api_dashboard_usuario'),
    path('reportes/<int:reporte_id>/', ReporteDetalleView.as_view(), name='api_reporte_detalle'),
    path('reportes/<int:reporte_id>/foto-url/', ReporteFotoUrlView.as_view(), name='api_reporte_foto_url'),
    path('s3/presigned-url/', S3PresignedUrlView.as_view(), name='api_s3_presigned_url'),
    path('reportes/<int:reporte_id>/estado/', ActualizarEstadoReporteView.as_view(), name='api_reporte_estado'),
    path('admin/dashboard/', DashboardMunicipalView.as_view(), name='api_admin_dashboard'),

    path('dispositivo/', RegistrarDispositivoView.as_view(), name='api_registrar_dispositivo'),
]