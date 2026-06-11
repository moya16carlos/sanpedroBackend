from django.utils import timezone

from django.shortcuts import render, get_object_or_404, redirect
from core.models import Reportes, Personas, Organizaciones
import os
import boto3
import uuid
from urllib.parse import urlparse
from core.models import Reportes, Personas, Organizaciones, HistorialReportes,Sectores,AuditoriaAdmin,DispositivosUsuario, NotificacionesEnviadas
from collections import Counter

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages



@login_required(login_url='dashboard_login')
def dashboard_home(request):
    return redirect('dashboard_vista_general')@login_required(login_url='dashboard_login')
def dashboard_home(request):
    return redirect('dashboard_vista_general')

@login_required(login_url='dashboard_login')
def dashboard_reportes(request):
    reportes = Reportes.objects.all().order_by('-fecha_creacion')

    q = request.GET.get('q')
    estado = request.GET.get('estado')

    if q:
        reportes = reportes.filter(titulo__icontains=q)

    if estado:
        reportes = reportes.filter(estado_municipio__icontains=estado)

    reportes = list(reportes)
    reportes = agregar_fotos_firmadas(reportes)

    return render(request, 'dashboard/reportes.html', {
        'reportes': reportes,
        'q': q or '',
        'estado': estado or '',
    })

def subir_archivo_s3(archivo, carpeta='reportes/san_pedro'):
    bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
    region_name = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')

    extension = archivo.name.split('.')[-1]
    key = f"{carpeta}/{uuid.uuid4()}.{extension}"

    s3_client = boto3.client(
        's3',
        region_name=region_name,
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    )

    s3_client.upload_fileobj(
        archivo,
        bucket_name,
        key,
        ExtraArgs={
            'ContentType': archivo.content_type
        }
    )

    return f"https://{bucket_name}.s3.amazonaws.com/{key}"



@login_required(login_url='dashboard_login')
def dashboard_reporte_detalle(request, reporte_id):
    reporte = get_object_or_404(Reportes, id=reporte_id)

    categorias_reporte = {
        'LUMINARIAS / ALUMBRADO': {
            'nombre': 'Luminarias / Alumbrado',
            'descripcion': 'Reportes de focos apagados, dañados o encendidos de día.',
            'icono': '💡',
            'color': '#eab308',
            'grupo': 'Municipalidad',
        },
        'CAMINOS Y CALLES': {
            'nombre': 'Caminos y Calles',
            'descripcion': 'Baches, eventos en el pavimento, grietas o caminos rurales dañados.',
            'icono': '🛣️',
            'color': '#f97316',
            'grupo': 'Municipalidad',
        },
        'MICROBASURALES / ASEO': {
            'nombre': 'Microbasurales / Aseo',
            'descripcion': 'Acumulación ilegal de basura o escombros en la vía pública.',
            'icono': '🗑️',
            'color': '#16a34a',
            'grupo': 'Municipalidad',
        },
        'SEGURIDAD CIUDADANA': {
            'nombre': 'Seguridad Ciudadana',
            'descripcion': 'Vehículos sospechosos, incivilidades o luminarias críticas apagadas.',
            'icono': '🛡️',
            'color': '#7c3aed',
            'grupo': 'Municipalidad',
        },
        'RUIDOS MOLESTOS': {
            'nombre': 'Ruidos Molestos',
            'descripcion': 'Denuncias por ruidos fuera de horario permitido.',
            'icono': '🔊',
            'color': '#dc2626',
            'grupo': 'Municipalidad',
        },
        'FUGA DE AGUA / ROTURA DE MATRIZ': {
            'nombre': 'Fuga de Agua / Rotura de Matriz',
            'descripcion': 'Pérdidas de agua masivas en la vía pública o matrices rotas.',
            'icono': '💧',
            'color': '#0891b2',
            'grupo': 'Agua Potable Rural',
        },
        'CORTE DE SUMINISTRO': {
            'nombre': 'Corte de Suministro',
            'descripcion': 'Interrupción total del servicio de agua potable en el medidor.',
            'icono': '🚱',
            'color': '#0ea5e9',
            'grupo': 'Agua Potable Rural',
        },
        'BAJA PRESIÓN': {
            'nombre': 'Baja Presión',
            'descripcion': 'Flujo de agua notoriamente deficiente en el arranque del hogar.',
            'icono': '🌊',
            'color': '#38bdf8',
            'grupo': 'Agua Potable Rural',
        },
        'CALIDAD DEL AGUA (TURBIEDAD)': {
            'nombre': 'Calidad del Agua (Turbiedad)',
            'descripcion': 'Agua sale con color, sedimentos o mal olor.',
            'icono': '🟤',
            'color': '#92400e',
            'grupo': 'Agua Potable Rural',
        },
        'SOLICITUD CAMIÓN ALJIBE': {
            'nombre': 'Solicitud Camión Aljibe',
            'descripcion': 'Petición de abastecimiento alternativo para emergencias.',
            'icono': '🚚',
            'color': '#1d4ed8',
            'grupo': 'Agua Potable Rural',
        },
        'OTRO': {
            'nombre': 'Otro',
            'descripcion': 'Cualquier otro requerimiento directo para la Municipalidad.',
            'icono': '⋯',
            'color': '#64748b',
            'grupo': 'General',
        },
    }

    def obtener_categoria(nombre_categoria):
        texto = (nombre_categoria or '').upper().strip()

        if texto in categorias_reporte:
            return categorias_reporte[texto]

        if 'LUMINARIA' in texto or 'ALUMBRADO' in texto or 'LUZ' in texto:
            return categorias_reporte['LUMINARIAS / ALUMBRADO']

        if 'CAMINO' in texto or 'CALLE' in texto or 'BACHE' in texto or 'PAVIMENTO' in texto:
            return categorias_reporte['CAMINOS Y CALLES']

        if 'BASURA' in texto or 'ASEO' in texto or 'MICROBASURAL' in texto or 'ESCOMBRO' in texto:
            return categorias_reporte['MICROBASURALES / ASEO']

        if 'SEGURIDAD' in texto or 'SOSPECHOSO' in texto or 'INCIVILIDAD' in texto:
            return categorias_reporte['SEGURIDAD CIUDADANA']

        if 'RUIDO' in texto or 'RUIDOS' in texto:
            return categorias_reporte['RUIDOS MOLESTOS']

        if 'FUGA' in texto or 'MATRIZ' in texto or 'ROTURA' in texto:
            return categorias_reporte['FUGA DE AGUA / ROTURA DE MATRIZ']

        if 'CORTE' in texto or 'SUMINISTRO' in texto:
            return categorias_reporte['CORTE DE SUMINISTRO']

        if 'PRESION' in texto or 'PRESIÓN' in texto:
            return categorias_reporte['BAJA PRESIÓN']

        if 'TURBIEDAD' in texto or 'CALIDAD' in texto or 'SEDIMENTO' in texto or 'OLOR' in texto:
            return categorias_reporte['CALIDAD DEL AGUA (TURBIEDAD)']

        if 'ALJIBE' in texto or 'CAMION' in texto or 'CAMIÓN' in texto:
            return categorias_reporte['SOLICITUD CAMIÓN ALJIBE']

        return categorias_reporte['OTRO']

    categoria = obtener_categoria(reporte.titulo)

    if request.method == 'POST':
        estado_validacion_anterior = reporte.estado_validacion
        estado_municipio_anterior = reporte.estado_municipio

        reporte.estado_validacion = request.POST.get(
            'estado_validacion',
            reporte.estado_validacion
        )

        reporte.estado_municipio = request.POST.get(
            'estado_municipio',
            reporte.estado_municipio
        )

        foto = request.FILES.get('foto')

        if foto:
            foto_url = subir_archivo_s3(foto)
            reporte.foto_url = foto_url

        reporte.save()

        if (
            estado_validacion_anterior != reporte.estado_validacion
            or estado_municipio_anterior != reporte.estado_municipio
        ):
            HistorialReportes.objects.create(
                reporte_id=reporte.id,
                accion='CAMBIO_ESTADO',
                detalle=(
                    f"Validación: {estado_validacion_anterior} → {reporte.estado_validacion}\n"
                    f"Municipio: {estado_municipio_anterior} → {reporte.estado_municipio}"
                )
            )

        if foto:
            HistorialReportes.objects.create(
                reporte_id=reporte.id,
                accion='SUBIDA_FOTO',
                detalle='Se agregó o reemplazó la fotografía del reporte.'
            )

        return redirect('dashboard_reporte_detalle', reporte_id=reporte.id)

    foto_firmada = generar_url_firmada_s3(reporte.foto_url)

    historial = HistorialReportes.objects.filter(
        reporte_id=reporte.id
    ).order_by('-fecha')

    sector = None
    autor = None



    try:
        autor = reporte.autor
    except:
        autor = None

    mapa_reporte = None

    if reporte.latitud and reporte.longitud:
        mapa_reporte = {
            'id': reporte.id,
            'latitud': float(reporte.latitud),
            'longitud': float(reporte.longitud),
            'titulo': reporte.descripcion or reporte.titulo or 'Sin título',
            'tipo': reporte.tipo or 'Sin tipo',
            'categoria': categoria['nombre'],
            'descripcion_categoria': categoria['descripcion'],
            'icono': categoria['icono'],
            'color_categoria': categoria['color'],
            'grupo_categoria': categoria['grupo'],
            'estado': reporte.estado_municipio or 'SIN_ESTADO',
        }

    return render(request, 'dashboard/reporte_detalle.html', {
        'reporte': reporte,
        'categoria': categoria,
        'sector': sector,
        'foto_firmada': foto_firmada,
        'historial': historial,
        'mapa_reporte': mapa_reporte,
        'autor': autor,
    })


@login_required(login_url='dashboard_login')
def dashboard_mapa(request):
    reportes = Reportes.objects.exclude(
        latitud__isnull=True
    ).exclude(
        longitud__isnull=True
    ).order_by('-fecha_creacion')

    puntos = []

    for reporte in reportes:
        estado = reporte.estado_municipio or 'SIN_ESTADO'

        if 'RESUELTO' in estado:
            color = 'green'
        elif 'PROCESO' in estado:
            color = 'blue'
        elif 'NO_ENVIADO' in estado:
            color = 'orange'
        else:
            color = 'gray'

        puntos.append({
            'id': reporte.id,
            'titulo': reporte.titulo or 'Sin título',
            'estado': estado,
            'latitud': float(reporte.latitud),
            'longitud': float(reporte.longitud),
            'color': color,
        })

    return render(request, 'dashboard/mapa.html', {
        'puntos': puntos,
    })

def generar_url_firmada_s3(foto_url):
    if not foto_url:
        return None

    bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
    region_name = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')

    parsed_url = urlparse(foto_url)
    key = parsed_url.path.lstrip('/')

    if not key:
        return None

    s3_client = boto3.client(
        's3',
        region_name=region_name,
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    )

    return s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket_name,
            'Key': key,
        },
        ExpiresIn=600
    )

def agregar_fotos_firmadas(reportes):
    for reporte in reportes:
        reporte.foto_firmada = generar_url_firmada_s3(reporte.foto_url)
    return reportes


# vistaa admin ###

from core.models import Personas, Sectores


@login_required(login_url='dashboard_login')
def dashboard_admin_panel(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')

        # CREAR SECTOR
        if accion == 'crear_sector':
            nombre_sector = request.POST.get('nombre_sector')

            if nombre_sector:
                Sectores.objects.create(
                    comuna_id=1,
                    nombre=nombre_sector.strip()
                )

                registrar_auditoria(
                    request,
                    'CREAR',
                    'Sectores',
                    f'Se creó el sector: {nombre_sector.strip()}'
                )

            return redirect('dashboard_admin_panel')

        # EDITAR SECTOR
        if accion == 'editar_sector':
            sector_id = request.POST.get('sector_id')
            nombre_sector = request.POST.get('nombre_sector')

            if sector_id and nombre_sector:
                Sectores.objects.filter(
                    id=sector_id
                ).update(
                    nombre=nombre_sector.strip()
                )

                registrar_auditoria(
                    request,
                    'EDITAR',
                    'Sectores',
                    f'Se editó el sector ID {sector_id}: {nombre_sector.strip()}'
                )

            return redirect('dashboard_admin_panel')

        # ELIMINAR SECTOR
        if accion == 'eliminar_sector':
            sector_id = request.POST.get('sector_id')

            if sector_id:
                sector = Sectores.objects.filter(id=sector_id).first()
                nombre_sector = sector.nombre if sector else 'Desconocido'

                Sectores.objects.filter(
                    id=sector_id
                ).delete()

                registrar_auditoria(
                    request,
                    'ELIMINAR',
                    'Sectores',
                    f'Se eliminó el sector ID {sector_id}: {nombre_sector}'
                )

            return redirect('dashboard_admin_panel')

        # CREAR ORGANIZACIÓN
        if accion == 'crear_organizacion':
            nombre = request.POST.get('nombre')
            tipo = request.POST.get('tipo')
            rut = request.POST.get('rut')
            sector_id = request.POST.get('sector_id')

            if nombre:
                Organizaciones.objects.create(
                    nombre=nombre.strip(),
                    tipo=tipo.strip() if tipo else None,
                    rut=rut.strip() if rut else None,
                    sector_id=sector_id if sector_id else None
                )

                registrar_auditoria(
                    request,
                    'CREAR',
                    'Organizaciones',
                    f'Se creó la organización: {nombre.strip()}'
                )

            return redirect('dashboard_admin_panel')

        # EDITAR ORGANIZACIÓN
        if accion == 'editar_organizacion':
            organizacion_id = request.POST.get('organizacion_id')
            nombre = request.POST.get('nombre')
            tipo = request.POST.get('tipo')
            rut = request.POST.get('rut')
            sector_id = request.POST.get('sector_id')

            if organizacion_id and nombre:
                Organizaciones.objects.filter(id=organizacion_id).update(
                    nombre=nombre.strip(),
                    tipo=tipo.strip() if tipo else None,
                    rut=rut.strip() if rut else None,
                    sector_id=sector_id if sector_id else None
                )

                registrar_auditoria(
                    request,
                    'EDITAR',
                    'Organizaciones',
                    f'Se editó la organización ID {organizacion_id}: {nombre.strip()}'
                )

            return redirect('dashboard_admin_panel')

        # ELIMINAR ORGANIZACIÓN
        if accion == 'eliminar_organizacion':
            organizacion_id = request.POST.get('organizacion_id')

            if organizacion_id:
                organizacion = Organizaciones.objects.filter(id=organizacion_id).first()
                nombre_org = organizacion.nombre if organizacion else 'Desconocida'

                Organizaciones.objects.filter(id=organizacion_id).delete()

                registrar_auditoria(
                    request,
                    'ELIMINAR',
                    'Organizaciones',
                    f'Se eliminó la organización ID {organizacion_id}: {nombre_org}'
                )

            return redirect('dashboard_admin_panel')

        # EDITAR USUARIO APP
        if accion == 'editar_usuario_app':
            usuario_id = request.POST.get('usuario_id')
            nombre = request.POST.get('nombre')
            email = request.POST.get('email')
            telefono = request.POST.get('telefono')
            sector_id = request.POST.get('sector_id')
           

            if usuario_id:
                Personas.objects.filter(id=usuario_id).update(
                    nombre=nombre.strip() if nombre else None,
                    email=email.strip() if email else None,
                    telefono=telefono.strip() if telefono else None,
                    sector_id=sector_id if sector_id else None,
               
                )

                registrar_auditoria(
                    request,
                    'EDITAR',
                    'Usuarios App',
                    f'Se editó el usuario app ID {usuario_id}: {nombre or "Sin nombre"}'
                )

            return redirect('dashboard_admin_panel')
        
        ## Notificaciones 
                # ENVIAR NOTIFICACIÓN
        if accion == 'enviar_notificacion':
            destinatario = request.POST.get('destinatario')
            sector_id = request.POST.get('sector_id')
            organizacion_id = request.POST.get('organizacion_id')
            titulo = request.POST.get('titulo')
            mensaje = request.POST.get('mensaje')

            total_destinatarios = 0

            if destinatario == 'todos':
                total_destinatarios = DispositivosUsuario.objects.filter(
                    activo=True
                ).count()

            elif destinatario == 'sector' and sector_id:
                personas_sector = Personas.objects.filter(
                    sector_id=sector_id
                ).values_list('id', flat=True)

                total_destinatarios = DispositivosUsuario.objects.filter(
                    persona_id__in=personas_sector,
                    activo=True
                ).count()

            elif destinatario == 'organizacion' and organizacion_id:
                total_destinatarios = 0

            # GUARDAR HISTORIAL
            NotificacionesEnviadas.objects.create(
                destinatario=destinatario,
                sector_id=sector_id if sector_id else None,
                organizacion_id=organizacion_id if organizacion_id else None,
                titulo=titulo,
                mensaje=mensaje,
                total_destinatarios=total_destinatarios,
                enviados=0,
                errores=0,
                fecha=timezone.now()
            )

            # AUDITORÍA
            registrar_auditoria(
                request,
                'ENVIAR',
                'Notificaciones',
                f'Notificación preparada: "{titulo}" para {destinatario}. Destinatarios estimados: {total_destinatarios}'
            )

            return redirect('dashboard_admin_panel')

    usuarios_app = Personas.objects.all().order_by('-id')

    sectores = Sectores.objects.all().order_by(
        'nombre'
    )

    organizaciones = Organizaciones.objects.all().order_by(
        'nombre'
    )

    logs_admin = AuditoriaAdmin.objects.all().order_by(
        '-fecha'
    )[:100]

    total_reportes = Reportes.objects.count()
    reportes_pendientes = Reportes.objects.filter(
        estado_validacion__icontains='PENDIENTE'
    ).count()
    reportes_en_proceso = Reportes.objects.filter(
        estado_municipio__icontains='PROCESO'
    ).count()
    reportes_resueltos = Reportes.objects.filter(
        estado_municipio__icontains='RESUELTO'
    ).count()

   
    total_dispositivos = DispositivosUsuario.objects.count()
    dispositivos_activos = DispositivosUsuario.objects.filter(activo=True).count()
    total_dispositivos = DispositivosUsuario.objects.count()

    notificaciones_enviadas = NotificacionesEnviadas.objects.all().order_by('-fecha')[:50]

    return render(
        request,
        'dashboard/admin_panel.html',
        {
            'usuarios_app': usuarios_app,
            'sectores': sectores,
            'organizaciones': organizaciones,
            'logs_admin': logs_admin,

            'total_usuarios_app': Personas.objects.count(),
            'total_sectores': Sectores.objects.count(),
            'total_organizaciones': Organizaciones.objects.count(),

            'total_reportes': total_reportes,
            'reportes_pendientes': reportes_pendientes,
            'reportes_en_proceso': reportes_en_proceso,
            'reportes_resueltos': reportes_resueltos,
            'total_dispositivos': total_dispositivos,
            'total_dispositivos': total_dispositivos,
            'dispositivos_activos': dispositivos_activos,
            'notificaciones_enviadas': notificaciones_enviadas,
        }
    )


@login_required(login_url='dashboard_login')
def dashboard_usuario_detalle(request, usuario_id):

    usuario = get_object_or_404(
        Personas,
        id=usuario_id
    )

    reportes_usuario = Reportes.objects.filter(
        autor_id=usuario.id
    ).order_by('-fecha_creacion')

    sector = None

    if usuario.sector_id:
        sector = Sectores.objects.filter(
            id=usuario.sector_id
        ).first()

    total_reportes = reportes_usuario.count()

    reportes_resueltos = reportes_usuario.filter(
        estado_municipio='RESUELTO'
    ).count()

    reportes_proceso = reportes_usuario.filter(
        estado_municipio__in=[
            'EN_PROCESO',
            'PROCESO'
        ]
    ).count()

    reportes_pendientes = (
        total_reportes
        - reportes_resueltos
        - reportes_proceso
    )

    return render(
        request,
        'dashboard/usuario_detalle.html',
        {
            'usuario': usuario,
            'sector': sector,
            'reportes_usuario': reportes_usuario,
            'total_reportes': total_reportes,
            'reportes_resueltos': reportes_resueltos,
            'reportes_proceso': reportes_proceso,
            'reportes_pendientes': reportes_pendientes,
        }
    )


### AUDITORIAS ###



def registrar_auditoria(request, accion, modulo, detalle):
    usuario = "Sistema"

    if request.user.is_authenticated:
        usuario = request.user.username

    ip = request.META.get('REMOTE_ADDR', '')

    AuditoriaAdmin.objects.create(
        accion=accion,
        modulo=modulo,
        detalle=detalle,
        usuario_sistema=usuario,
        ip=ip
    )

####logins##

def dashboard_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard_home')

        messages.error(request, 'Correo o contraseña incorrectos.')

    return render(request, 'dashboard/login.html')


def dashboard_logout(request):
    logout(request)
    return redirect('dashboard_login')


### VISTA GENERAL ####
@login_required(login_url='dashboard_login')
def dashboard_vista_general(request):
    reportes = Reportes.objects.select_related('autor').all().order_by('-fecha_creacion')
    total_reportes = reportes.count()
    usuarios = Personas.objects.all()
    organizaciones = Organizaciones.objects.all()
    sectores = Sectores.objects.all()

    resueltos = reportes.filter(
        estado_municipio='RESUELTO'
    ).count()

    en_proceso = reportes.filter(
        estado_municipio__in=[
            'EN_PROCESO',
            'PROCESO'
        ]
    ).count()

    pendientes = reportes.exclude(
        estado_municipio='RESUELTO'
    ).exclude(
        estado_municipio__in=[
            'EN_PROCESO',
            'PROCESO'
        ]
    ).count()

    max_bar_height = 140

    altura_resueltos = 0
    altura_proceso = 0
    altura_pendientes = 0
    
     

    if int(total_reportes) > 0:
        altura_resueltos = max(
            10,
            int((resueltos / total_reportes) * max_bar_height)
        )

        altura_proceso = max(
            10,
            int((en_proceso / total_reportes) * max_bar_height)
        )

        altura_pendientes = max(
            10,
            int((pendientes / total_reportes) * max_bar_height)
        )

    categorias_reporte = [
        {
            'nombre': 'Luminarias / Alumbrado',
            'descripcion': 'Reportes de focos apagados, dañados o encendidos de día.',
            'icono': '💡',
            'color': '#eab308',
            'grupo': 'Municipalidad',
        },
        {
            'nombre': 'Caminos y Calles',
            'descripcion': 'Baches, eventos en el pavimento, grietas o caminos rurales dañados.',
            'icono': '🛣️',
            'color': '#f97316',
            'grupo': 'Municipalidad',
        },
        {
            'nombre': 'Microbasurales / Aseo',
            'descripcion': 'Acumulación ilegal de basura o escombros en la vía pública.',
            'icono': '🗑️',
            'color': '#16a34a',
            'grupo': 'Municipalidad',
        },
        {
            'nombre': 'Seguridad Ciudadana',
            'descripcion': 'Vehículos sospechosos, incivilidades o luminarias críticas apagadas.',
            'icono': '🛡️',
            'color': '#7c3aed',
            'grupo': 'Municipalidad',
        },
        {
            'nombre': 'Ruidos Molestos',
            'descripcion': 'Denuncias por ruidos fuera de horario permitido.',
            'icono': '🔊',
            'color': '#dc2626',
            'grupo': 'Municipalidad',
        },
        {
            'nombre': 'Fuga de Agua / Rotura de Matriz',
            'descripcion': 'Pérdidas de agua masivas en la vía pública o matrices rotas.',
            'icono': '💧',
            'color': '#0891b2',
            'grupo': 'Agua Potable Rural',
        },
        {
            'nombre': 'Corte de Suministro',
            'descripcion': 'Interrupción total del servicio de agua potable en el medidor.',
            'icono': '🚱',
            'color': '#0ea5e9',
            'grupo': 'Agua Potable Rural',
        },
        {
            'nombre': 'Baja Presión',
            'descripcion': 'Flujo de agua notoriamente deficiente en el arranque del hogar.',
            'icono': '🌊',
            'color': '#38bdf8',
            'grupo': 'Agua Potable Rural',
        },
        {
            'nombre': 'Calidad del Agua (Turbiedad)',
            'descripcion': 'Agua sale con color, sedimentos o mal olor.',
            'icono': '🟤',
            'color': '#92400e',
            'grupo': 'Agua Potable Rural',
        },
        {
            'nombre': 'Solicitud Camión Aljibe',
            'descripcion': 'Petición de abastecimiento alternativo para emergencias.',
            'icono': '🚚',
            'color': '#1d4ed8',
            'grupo': 'Agua Potable Rural',
        },
        {
            'nombre': 'Otro',
            'descripcion': 'Cualquier otro requerimiento directo para la Municipalidad.',
            'icono': '⋯',
            'color': '#64748b',
            'grupo': 'General',
        },
    ]

    def obtener_categoria(nombre_categoria):
        texto = (nombre_categoria or '').upper().strip()

        for categoria in categorias_reporte:
            nombre = categoria['nombre'].upper()

            if texto == nombre or nombre in texto or texto in nombre:
                return categoria

        if 'LUMINARIA' in texto or 'LUMINARIAS' in texto or 'ALUMBRADO' in texto or 'LUZ' in texto:
            return categorias_reporte[0]

        if 'CAMINO' in texto or 'CALLE' in texto or 'BACHE' in texto or 'PAVIMENTO' in texto:
            return categorias_reporte[1]

        if 'BASURA' in texto or 'ASEO' in texto or 'MICROBASURAL' in texto or 'ESCOMBRO' in texto:
            return categorias_reporte[2]

        if 'SEGURIDAD' in texto or 'SOSPECHOSO' in texto or 'INCIVILIDAD' in texto:
            return categorias_reporte[3]

        if 'RUIDO' in texto or 'RUIDOS' in texto:
            return categorias_reporte[4]

        if 'FUGA' in texto or 'MATRIZ' in texto or 'ROTURA' in texto:
            return categorias_reporte[5]

        if 'CORTE' in texto or 'SUMINISTRO' in texto:
            return categorias_reporte[6]

        if 'PRESION' in texto or 'PRESIÓN' in texto:
            return categorias_reporte[7]

        if 'TURBIEDAD' in texto or 'CALIDAD' in texto or 'SEDIMENTO' in texto or 'OLOR' in texto:
            return categorias_reporte[8]

        if 'ALJIBE' in texto or 'CAMION' in texto or 'CAMIÓN' in texto:
            return categorias_reporte[9]

        return categorias_reporte[-1]

    puntos_mapa = []

    reportes_con_ubicacion = reportes.exclude(
        latitud__isnull=True
    ).exclude(
        longitud__isnull=True
    )

    for reporte in reportes_con_ubicacion:
        estado = reporte.estado_municipio or 'SIN_ESTADO'

        # En tu base, la categoría real viene en titulo.
        # El campo tipo guarda Municipalidad o APR.
        categoria = obtener_categoria(reporte.titulo)

        puntos_mapa.append({
            'id': reporte.id,
            'titulo': reporte.descripcion or reporte.titulo or 'Sin título',
            'tipo': reporte.tipo or 'Sin tipo',
            'categoria': categoria['nombre'],
            'descripcion_categoria': categoria['descripcion'],
            'icono': categoria['icono'],
            'color_categoria': categoria['color'],
            'grupo_categoria': categoria['grupo'],
            'estado': estado,
            'latitud': float(reporte.latitud),
            'longitud': float(reporte.longitud),
        })

    solicitudes_servicio = reportes.filter(
        titulo__icontains='Solicitud'
    )[:10]

    notificaciones = NotificacionesEnviadas.objects.all().order_by('-fecha')[:50]

    for noti in notificaciones:
        noti.destino_nombre = "Toda la comuna"

        if noti.destinatario == 'sector' and noti.sector_id:
            sector = Sectores.objects.filter(id=noti.sector_id).first()
            if sector:
                noti.destino_nombre = sector.nombre

        elif noti.destinatario == 'organizacion' and noti.organizacion_id:
            org = Organizaciones.objects.filter(id=noti.organizacion_id).first()
            if org:
                noti.destino_nombre = org.nombre

    top_tipos_reportes = Counter(
        [(r.titulo or 'Sin categoría') for r in reportes]
    ).most_common(5)

    reportes_criticos = reportes.exclude(
        estado_municipio__icontains='RESUELTO'
    ).order_by('-fecha_creacion')[:5]

    return render(request, 'dashboard/vista_general.html', {
        'total_usuarios': usuarios.count(),
        'total_organizaciones': organizaciones.count(),
        'total_reportes': total_reportes,
        'resueltos': resueltos,
        'en_proceso': en_proceso,
        'pendientes': pendientes,
        'ultimos_reportes': reportes[:10],
        'top_tipos_reportes': top_tipos_reportes,
        'sectores': sectores,
        'organizaciones': organizaciones,
        'nota_promedio': 0,
        'puntos_mapa': puntos_mapa,
        'categorias_reporte': categorias_reporte,
        'solicitudes_servicio': solicitudes_servicio,
        'notificaciones': notificaciones,
        'total_notificaciones': NotificacionesEnviadas.objects.count(),
        'reportes_criticos': reportes_criticos,
        'altura_resueltos': altura_resueltos,
        'altura_proceso': altura_proceso,
        'altura_pendientes': altura_pendientes,
    })


#### vista admin TI ####

from core.models import AccesoFuncionario


@login_required(login_url='dashboard_login')
def dashboard_admin_ti(request):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, "No tienes permisos para acceder al panel TI.")
        return redirect('dashboard_home')

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'crear_acceso':
            email = request.POST.get('email', '').strip().lower()
            nombre = request.POST.get('nombre', '').strip()
            rol = request.POST.get('rol', 'FUNCIONARIO')
            activo = request.POST.get('activo') == 'on'

            if email:
                acceso, creado = AccesoFuncionario.objects.update_or_create(
                    email=email,
                    defaults={
                        'nombre': nombre,
                        'rol': rol,
                        'activo': activo,
                    }
                )

                if creado:
                    messages.success(request, f"Acceso creado para {email}.")
                else:
                    messages.success(request, f"Acceso actualizado para {email}.")
            else:
                messages.error(request, "Debes ingresar un correo electrónico.")

            return redirect('dashboard_admin_ti')

        if accion == 'desactivar':
            acceso_id = request.POST.get('acceso_id')
            acceso = get_object_or_404(AccesoFuncionario, id=acceso_id)
            acceso.activo = False
            acceso.save()
            messages.success(request, f"Acceso desactivado para {acceso.email}.")
            return redirect('dashboard_admin_ti')

        if accion == 'activar':
            acceso_id = request.POST.get('acceso_id')
            acceso = get_object_or_404(AccesoFuncionario, id=acceso_id)
            acceso.activo = True
            acceso.save()
            messages.success(request, f"Acceso activado para {acceso.email}.")
            return redirect('dashboard_admin_ti')

        if accion == 'eliminar':
            acceso_id = request.POST.get('acceso_id')
            acceso = get_object_or_404(AccesoFuncionario, id=acceso_id)
            email = acceso.email
            acceso.delete()
            messages.success(request, f"Acceso eliminado para {email}.")
            return redirect('dashboard_admin_ti')

    accesos = AccesoFuncionario.objects.all().order_by('-id')

    usuarios_app = Personas.objects.all().order_by('nombre')

    auditorias = AuditoriaAdmin.objects.all().order_by('-id')[:100]

    return render(request, 'dashboard/admin_ti.html', {
        'accesos': accesos,
        'total_accesos': accesos.count(),
        'total_activos': accesos.filter(activo=True).count(),
        'total_inactivos': accesos.filter(activo=False).count(),
        'usuarios_app': usuarios_app,
        'total_usuarios_app': usuarios_app.count(),
        'auditorias': auditorias,
    })