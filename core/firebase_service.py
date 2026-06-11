import os
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings


def inicializar_firebase():
    if not firebase_admin._apps:
        cred_path = os.path.join(settings.BASE_DIR, "firebase", "serviceAccountKey.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)


def enviar_push_token(token, titulo, mensaje, data=None):
    inicializar_firebase()

    message = messaging.Message(
        notification=messaging.Notification(
            title=titulo,
            body=mensaje,
        ),
        data=data or {},
        token=token,
    )

    return messaging.send(message)