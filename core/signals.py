from django.db.models.signals import pre_save
from django.dispatch import receiver

from core.models import Reportes, DispositivosUsuario
from core.firebase_service import enviar_push_token


@receiver(pre_save, sender=Reportes)
def notificar_cambio_estado_reporte(sender, instance, **kwargs):

    if not instance.pk:
        return

    try:
        anterior = Reportes.objects.get(pk=instance.pk)
    except Reportes.DoesNotExist:
        return

    print("\n==============================")
    print("REPORTE MODIFICADO")
    print("ID:", instance.id)
    print("AUTOR:", instance.autor_id)
    print("==============================\n")

    if not instance.autor_id:
        print("ERROR: El reporte no tiene autor_id")
        return

    dispositivos = DispositivosUsuario.objects.filter(
        persona_id=instance.autor_id,
        activo=True
    )

    print("DISPOSITIVOS ENCONTRADOS:", dispositivos.count())

    if not dispositivos.exists():
        print("ERROR: No existen dispositivos activos para esta persona")
        return

    # CAMBIO ESTADO MUNICIPAL
    if anterior.estado_municipio != instance.estado_municipio:

        print(
            f"CAMBIO estado_municipio: "
            f"{anterior.estado_municipio} -> {instance.estado_municipio}"
        )

        for dispositivo in dispositivos:

            print(
                f"ENVIANDO PUSH A TOKEN: "
                f"{dispositivo.fcm_token[:40]}..."
            )

            try:
                resultado = enviar_push_token(
                    token=dispositivo.fcm_token,
                    titulo="Estado municipal actualizado",
                    mensaje=f"Tu reporte '{instance.titulo}' cambió a: {instance.estado_municipio}",
                    data={
                        "tipo": "estado_municipio",
                        "reporte_id": str(instance.id),
                        "estado_anterior": str(anterior.estado_municipio or ""),
                        "estado_nuevo": str(instance.estado_municipio or ""),
                    }
                )

                print("PUSH ENVIADA OK:", resultado)

            except Exception as e:
                print("ERROR PUSH:", str(e))

    # CAMBIO ESTADO VALIDACION
    if anterior.estado_validacion != instance.estado_validacion:

        print(
            f"CAMBIO estado_validacion: "
            f"{anterior.estado_validacion} -> {instance.estado_validacion}"
        )

        for dispositivo in dispositivos:

            print(
                f"ENVIANDO PUSH A TOKEN: "
                f"{dispositivo.fcm_token[:40]}..."
            )

            try:
                resultado = enviar_push_token(
                    token=dispositivo.fcm_token,
                    titulo="Validación actualizada",
                    mensaje=f"Tu reporte '{instance.titulo}' ahora está: {instance.estado_validacion}",
                    data={
                        "tipo": "estado_validacion",
                        "reporte_id": str(instance.id),
                        "estado_anterior": str(anterior.estado_validacion or ""),
                        "estado_nuevo": str(instance.estado_validacion or ""),
                    }
                )

                print("PUSH ENVIADA OK:", resultado)

            except Exception as e:
                print("ERROR PUSH:", str(e))