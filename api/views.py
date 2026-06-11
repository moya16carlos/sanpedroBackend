from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.models import (
    Comunas, Sectores, Cargos, Organizaciones,
    Personas, Reportes, DispositivosUsuario
)

from .serializers import (
    ComunasSerializer, SectoresSerializer, CargosSerializer,
    OrganizacionesSerializer, PersonasSerializer, ReportesSerializer
)


class ComunasListView(generics.ListAPIView):
    serializer_class = ComunasSerializer

    def get_queryset(self):
        return Comunas.objects.filter(contrato_activo=True).order_by('nombre')


class SectoresListView(generics.ListAPIView):
    serializer_class = SectoresSerializer

    def get_queryset(self):
        queryset = Sectores.objects.all().order_by('nombre')
        comuna_id = self.request.query_params.get('comuna_id')

        if comuna_id:
            queryset = queryset.filter(comuna_id=comuna_id)

        return queryset


class CargosListView(generics.ListAPIView):
    serializer_class = CargosSerializer
    queryset = Cargos.objects.all().order_by('id')


class OrganizacionesListView(generics.ListAPIView):
    serializer_class = OrganizacionesSerializer

    def get_queryset(self):
        queryset = Organizaciones.objects.all().order_by('nombre')
        sector_id = self.request.query_params.get('sector_id')

        if sector_id:
            queryset = queryset.filter(sector_id=sector_id)

        return queryset


class RegistroPersonaView(generics.CreateAPIView):
    serializer_class = PersonasSerializer
    queryset = Personas.objects.all()

    def create(self, request, *args, **kwargs):
        rut = request.data.get('rut')

        if rut and Personas.objects.filter(rut=rut).exists():
            return Response(
                {'error': 'Ya existe una persona registrada con este RUT'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        persona = serializer.save()

        return Response({
            'mensaje': 'Registro exitoso',
            'persona_id': persona.id,
            'persona': serializer.data
        }, status=status.HTTP_201_CREATED)


class PerfilPersonaView(APIView):
    def get(self, request):
        rut = request.query_params.get('rut')
        persona_id = request.query_params.get('id')

        if not rut and not persona_id:
            return Response(
                {'error': 'Debes enviar rut o id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if persona_id:
                persona = Personas.objects.get(id=persona_id)
            else:
                persona = Personas.objects.get(rut=rut)

            serializer = PersonasSerializer(persona)

            return Response({
                'mensaje': 'Perfil encontrado',
                'persona': serializer.data
            })

        except Personas.DoesNotExist:
            return Response(
                {'error': 'Persona no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )


class ReportesListCreateView(generics.ListCreateAPIView):
    serializer_class = ReportesSerializer

    def get_queryset(self):
        queryset = Reportes.objects.all().order_by('-fecha_creacion')

        autor_id = self.request.query_params.get('autor_id')
        rut = self.request.query_params.get('rut')

        if autor_id:
            queryset = queryset.filter(autor_id=autor_id)

        if rut:
            queryset = queryset.filter(autor__rut=rut)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        if not data.get('autor') and data.get('rut'):
            try:
                persona = Personas.objects.get(rut=data.get('rut'))
                data['autor'] = persona.id
            except Personas.DoesNotExist:
                return Response(
                    {'error': 'No existe una persona registrada con ese RUT'},
                    status=status.HTTP_404_NOT_FOUND
                )

        data.setdefault('tipo', 'GENERICO')
        data.setdefault('estado_validacion', 'PENDIENTE_DIRIGENTE')
        data.setdefault('estado_municipio', 'NO_ENVIADO')
        data.setdefault('es_visitante', 0)
        data['fecha_creacion'] = timezone.now()

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        reporte = serializer.save()

        return Response({
            'mensaje': 'Reporte creado exitosamente',
            'reporte_id': reporte.id,
            'reporte': serializer.data
        }, status=status.HTTP_201_CREATED)
    

import secrets
from django.utils import timezone

class LoginGoogleView(APIView):
    def post(self, request):
        auth_id = request.data.get('auth_id')
        email = request.data.get('email')
        nombre = request.data.get('nombre')
        rut = request.data.get('rut')
        comuna_id = request.data.get('comuna_id')
        sector_id = request.data.get('sector_id')

        if not auth_id or not email:
            return Response(
                {'error': 'auth_id y email son obligatorios'},
                status=status.HTTP_400_BAD_REQUEST
            )

        persona = Personas.objects.filter(auth_id=auth_id).first()

        if not persona and email:
            persona = Personas.objects.filter(email=email).first()

        if not persona and rut:
            persona = Personas.objects.filter(rut=rut).first()

        if not persona:
            persona = Personas.objects.create(
                metodo_auth='google',
                auth_id=auth_id,
                email=email,
                nombre=nombre or email,
                rut=rut,
                comuna_id=comuna_id or 1,
                sector_id=sector_id or 1,
                identidad_validada=False,
                fecha_registro=timezone.now(),
                ultimo_acceso=timezone.now(),
            )
        else:
            persona.metodo_auth = 'google'
            persona.auth_id = auth_id
            persona.email = email or persona.email
            persona.nombre = nombre or persona.nombre
            persona.ultimo_acceso = timezone.now()

            update_fields = ['metodo_auth', 'auth_id', 'ultimo_acceso']

            if email:
                update_fields.append('email')

            if nombre:
                update_fields.append('nombre')

            if comuna_id:
                persona.comuna_id = comuna_id
                update_fields.append('comuna_id')

            if sector_id:
                persona.sector_id = sector_id
                update_fields.append('sector_id')

            persona.save(update_fields=update_fields)

        serializer = PersonasSerializer(persona)

        return Response({
            'mensaje': 'Login con Google exitoso',
            'token': auth_id,
            'persona_id': persona.id,
            'requiere_completar_perfil': not bool(persona.rut),
            'persona': serializer.data
        })
    
class PerfilActualView(APIView):

    def obtener_token(self, request):
        token = request.query_params.get('token')

        if not token:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.replace('Bearer ', '').strip()

        return token

    def get(self, request):
        token = self.obtener_token(request)

        if not token:
            return Response(
                {'error': 'Token no enviado'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            persona = Personas.objects.get(auth_id=token)
        except Personas.DoesNotExist:
            return Response(
                {'error': 'Token inválido'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = PersonasSerializer(persona)

        return Response({
            'mensaje': 'Perfil actual',
            'persona': serializer.data
        })

    def put(self, request):
        token = self.obtener_token(request)

        if not token:
            return Response(
                {'error': 'Token no enviado'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            persona = Personas.objects.get(auth_id=token)
        except Personas.DoesNotExist:
            return Response(
                {'error': 'Token inválido'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        campos_permitidos = [
            'nombre',
            'rut',
            'genero',
            'telefono',
            'email',
            'comuna_id',
            'sector_id',
        ]

        for campo in campos_permitidos:
            if campo in request.data:
                setattr(persona, campo, request.data.get(campo))

        persona.save()

        serializer = PersonasSerializer(persona)

        return Response({
            'mensaje': 'Perfil actualizado correctamente',
            'persona': serializer.data
        })
    

class MisReportesView(APIView):
    def get(self, request):
        token = request.query_params.get('token')

        if not token:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.replace('Bearer ', '').strip()

        if not token:
            return Response(
                {'error': 'Token no enviado'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            persona = Personas.objects.get(auth_id=token)
        except Personas.DoesNotExist:
            return Response(
                {'error': 'Token inválido'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        reportes = Reportes.objects.filter(autor=persona).order_by('-fecha_creacion')
        serializer = ReportesSerializer(reportes, many=True)

        return Response({
            'mensaje': 'Mis reportes',
            'persona_id': persona.id,
            'total': reportes.count(),
            'reportes': serializer.data
        })
    

class DashboardUsuarioView(APIView):
    def get(self, request):
        token = request.query_params.get('token')

        if not token:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.replace('Bearer ', '').strip()

        if not token:
            return Response(
                {'error': 'Token no enviado'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            persona = Personas.objects.get(auth_id=token)
        except Personas.DoesNotExist:
            return Response(
                {'error': 'Token inválido'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        reportes = Reportes.objects.filter(autor=persona)

        total = reportes.count()
        pendientes = reportes.filter(estado_validacion__icontains='PENDIENTE').count()
        en_proceso = reportes.filter(estado_municipio__icontains='PROCESO').count()
        resueltos = reportes.filter(estado_municipio__icontains='RESUELTO').count()

        ultimos_reportes = reportes.order_by('-fecha_creacion')[:5]
        serializer = ReportesSerializer(ultimos_reportes, many=True)

        return Response({
            'mensaje': 'Dashboard usuario',
            'persona': {
                'id': persona.id,
                'nombre': persona.nombre,
                'rut': persona.rut,
                'email': persona.email,
            },
            'resumen': {
                'total_reportes': total,
                'pendientes': pendientes,
                'en_proceso': en_proceso,
                'resueltos': resueltos,
            },
            'ultimos_reportes': serializer.data
        })
    

class ReporteDetalleView(APIView):

    def get(self, request, reporte_id):
        try:
            reporte = Reportes.objects.get(id=reporte_id)
        except Reportes.DoesNotExist:
            return Response(
                {'error': 'Reporte no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ReportesSerializer(reporte)

        return Response({
            'mensaje': 'Detalle del reporte',
            'reporte': serializer.data
        })

    def put(self, request, reporte_id):
        try:
            reporte = Reportes.objects.get(id=reporte_id)
        except Reportes.DoesNotExist:
            return Response(
                {'error': 'Reporte no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        campos_permitidos = [
            'tipo',
            'titulo',
            'descripcion',
            'latitud',
            'longitud',
            'foto_url',
            'estado_validacion',
            'estado_municipio',
            'es_visitante',
        ]

        for campo in campos_permitidos:
            if campo in request.data:
                setattr(reporte, campo, request.data.get(campo))

        reporte.save()

        serializer = ReportesSerializer(reporte)

        return Response({
            'mensaje': 'Reporte actualizado correctamente',
            'reporte': serializer.data
        })
    

class ReporteFotoUrlView(APIView):
    def post(self, request, reporte_id):
        foto_url = request.data.get('foto_url')

        if not foto_url:
            return Response(
                {'error': 'Debes enviar foto_url'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            reporte = Reportes.objects.get(id=reporte_id)
        except Reportes.DoesNotExist:
            return Response(
                {'error': 'Reporte no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        reporte.foto_url = foto_url
        reporte.save(update_fields=['foto_url'])

        serializer = ReportesSerializer(reporte)

        return Response({
            'mensaje': 'Foto agregada correctamente',
            'reporte': serializer.data
        })

import os
import uuid
import boto3

class S3PresignedUrlView(APIView):
    def post(self, request):
        filename = request.data.get('filename', 'foto.jpg')
        content_type = request.data.get('content_type', 'image/jpeg')
        carpeta = request.data.get('carpeta', 'reportes/san_pedro')

        bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
        region_name = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')

        extension = filename.split('.')[-1] if '.' in filename else 'jpg'
        key = f"{carpeta}/{uuid.uuid4()}.{extension}"

        s3_client = boto3.client(
            's3',
            region_name=region_name,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )

        upload_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': key,
                'ContentType': content_type,
            },
            ExpiresIn=300
        )

        public_url = f"https://{bucket_name}.s3.amazonaws.com/{key}"

        return Response({
            'mensaje': 'URL generada correctamente',
            'upload_url': upload_url,
            'public_url': public_url,
            'key': key
        })
    
class ActualizarEstadoReporteView(APIView):
    def put(self, request, reporte_id):
        try:
            reporte = Reportes.objects.get(id=reporte_id)
        except Reportes.DoesNotExist:
            return Response(
                {'error': 'Reporte no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        estado_validacion = request.data.get('estado_validacion')
        estado_municipio = request.data.get('estado_municipio')
        validador_id = request.data.get('validador_id')

        if estado_validacion:
            reporte.estado_validacion = estado_validacion

        if estado_municipio:
            reporte.estado_municipio = estado_municipio

        if validador_id:
            reporte.validador_id = validador_id

        reporte.save()

        serializer = ReportesSerializer(reporte)

        return Response({
            'mensaje': 'Estado del reporte actualizado correctamente',
            'reporte': serializer.data
        })


class DashboardMunicipalView(APIView):
    def get(self, request):
        reportes = Reportes.objects.all()

        total = reportes.count()
        pendientes = reportes.filter(estado_validacion__icontains='PENDIENTE').count()
        no_enviados = reportes.filter(estado_municipio__icontains='NO_ENVIADO').count()
        en_proceso = reportes.filter(estado_municipio__icontains='PROCESO').count()
        resueltos = reportes.filter(estado_municipio__icontains='RESUELTO').count()

        ultimos_reportes = reportes.order_by('-fecha_creacion')[:10]
        serializer = ReportesSerializer(ultimos_reportes, many=True)

        return Response({
            'mensaje': 'Dashboard municipal',
            'resumen': {
                'total_reportes': total,
                'pendientes_validacion': pendientes,
                'no_enviados': no_enviados,
                'en_proceso': en_proceso,
                'resueltos': resueltos,
            },
            'ultimos_reportes': serializer.data
        })
    
## NOTIFICACIONES PUSH ##

class RegistrarDispositivoView(APIView):
    def post(self, request):
        persona_id = request.data.get('persona_id')
        fcm_token = request.data.get('fcm_token')
        plataforma = request.data.get('plataforma', 'android')

        if not persona_id or not fcm_token:
            return Response(
                {'error': 'persona_id y fcm_token son obligatorios'},
                status=400
            )

        dispositivo, creado = DispositivosUsuario.objects.update_or_create(
            fcm_token=fcm_token,
            defaults={
                'persona_id': persona_id,
                'plataforma': plataforma,
                'activo': True,
                'ultimo_acceso': timezone.now(),
            }
        )

        return Response({
            'mensaje': 'Dispositivo registrado correctamente',
            'creado': creado,
            'dispositivo_id': dispositivo.id
        })