# services.py
# Los servicios son funciones que contienen la lógica de negocio.
# Se separan de las views para mantener el código ordenado y limpio.
# La idea es: las views reciben la petición, los services hacen el trabajo.

from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Notification, NotificationUser


def get_unread_notifications(user_id: int):
    # Esta función recibe el ID de un usuario y regresa
    # todas sus notificaciones que todavía no ha leído.
    return (
        Notification.objects.filter(
            user_statuses__user_id=user_id,
            user_statuses__is_read=False,
            is_deleted=False,
        )
        .order_by("-created_at")
    )


def mark_notification_as_read(user_id: int, notification_id: int):
    # Esta función marca una notificación como leída para un usuario.
    # 1. Idempotencia: si la llamas dos veces no rompe nada.
    # 2. Registra read_at: guarda exactamente cuándo fue leída.
    # 3. Seguridad: si la notificación no pertenece al usuario da 404.
    notification_user = get_object_or_404(
        NotificationUser,
        notification_id=notification_id,
        user_id=user_id,
    )

    if not notification_user.is_read:
        notification_user.is_read = True
        notification_user.read_at = timezone.now()
        notification_user.save(update_fields=["is_read", "read_at"])

    return notification_user


def create_notification_for_users(title: str, message: str, user_ids: list):
    # Crea una notificación y la distribuye a varios usuarios.
    # Es llamada desde tasks.py para ejecutarse en background con Celery.
    notification = Notification.objects.create(
        title=title,
        message=message
    )

    # bulk_create inserta todos los registros en una sola query
    # en vez de hacer una query por cada usuario. Mucho más eficiente.
    NotificationUser.objects.bulk_create([
        NotificationUser(
            notification=notification,
            user_id=uid
        )
        for uid in user_ids
    ])

    return notification