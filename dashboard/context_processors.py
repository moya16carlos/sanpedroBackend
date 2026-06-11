from core.models import AccesoFuncionario


def acceso_funcionario(request):
    acceso = None

    if request.user.is_authenticated and request.user.email:
        acceso = AccesoFuncionario.objects.filter(
            email__iexact=request.user.email,
            activo=True
        ).first()

    return {
        'acceso_funcionario': acceso,
    }