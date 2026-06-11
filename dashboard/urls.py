from django.urls import path

from .views import (
    dashboard_home,
    dashboard_reportes,
    dashboard_reporte_detalle,
    dashboard_mapa,
    dashboard_usuario_detalle,
    dashboard_admin_panel,
    dashboard_login,
    dashboard_logout,
    dashboard_vista_general,
    dashboard_admin_ti
)

urlpatterns = [
    path('', dashboard_vista_general, name='dashboard_home'),
    path('reportes/', dashboard_reportes, name='dashboard_reportes'),
    path('reportes/<int:reporte_id>/', dashboard_reporte_detalle, name='dashboard_reporte_detalle'),
    path('mapa/', dashboard_mapa, name='dashboard_mapa'),
    path('admin-panel/usuario/<int:usuario_id>/', dashboard_usuario_detalle, name='dashboard_usuario_detalle'),
    
    path('admin-panel/', dashboard_admin_panel, name='dashboard_admin_panel'),
    path('login/', dashboard_login, name='dashboard_login'),
    path('logout/', dashboard_logout, name='dashboard_logout'),

    path('admin-ti/', dashboard_admin_ti, name='dashboard_admin_ti'),




    
]