from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import PermissionDenied
from .models import AccesoFuncionario


class GoogleAccessAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        email = sociallogin.user.email

        if not email:
            raise PermissionDenied("No se pudo obtener el correo de Google.")

        permitido = AccesoFuncionario.objects.filter(
            email__iexact=email,
            activo=True
        ).exists()

        if not permitido:
            raise PermissionDenied(
                "Este correo no tiene acceso autorizado al panel."
            )