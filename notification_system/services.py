# Los servicios son funciones que contienen la lógica de negocio.
# Se separan de las views para mantener el código ordenado y limpio.
# La idea es: las views reciben la petición, los services hacen el trabajo.

from django.utils import timezone
from django.shortcuts import get_object_or_404

from ..notifications.models import Notification, NotificationUser

def get_unread_notifications(user_id: int):
    # Esta función recibe el ID de un usuario y regresa
    # todas sus notificaciones que todavía no ha leído.
    #
    # Usamos el ORM de Django (no SQL crudo) porque es más
    # fácil de leer y funciona con cualquier base de datos.
    # ORM significa que en vez de escribir:
    #   SELECT * FROM notifications WHERE user_id = 1 AND is_read = False
    # escribimos código Python normal y Django lo convierte a SQL solo.

      return (
        Notification.objects.filter(
            # Filtramos por el usuario que nos pasaron
            user_statuses__user_id=user_id,
            # Solo las que NO ha leído
            user_statuses__is_read=False,
            # Excluimos las que fueron borradas lógicamente
            is_deleted=False,
        )
        .order_by("-created_at")  # Las más nuevas primero
    )
      
def mark_notification_as_read(user_id: int, notification_id: int):
    # Esta función marca una notificación como leída para un usuario.
    #
    # Tiene tres garantías importantes:
    # 1. Idempotencia: si la llamas dos veces con los mismos datos,
    #    el resultado es el mismo. No va a romper nada si se llama de más.
    # 2. Registra read_at: guarda exactamente cuándo fue leída.
    # 3. Seguridad: si la notificación no le pertenece al usuario,
    #    regresa un error 404 en vez de dejar que la marque.

    # Buscamos el registro que une a este usuario con esta notificación.
    # Si no existe (la notificación no fue enviada a este usuario),
    # get_object_or_404 lanza automáticamente un error 404.
    notification_user = get_object_or_404(
        NotificationUser,
        notification_id=notification_id,
        user_id=user_id,
    )
    # Solo actualizamos si todavía no estaba leída.
    # Esto es lo que garantiza la idempotencia:
    # si ya estaba leída, no hacemos nada y regresamos el objeto tal cual.
    # Así evitamos sobrescribir la fecha original de lectura.
    if not notification_user.is_read:
        notification_user.is_read = True
        notification_user.read_at = timezone.now()
        notification_user.save(update_fields=["is_read", "read_at"])

    return notification_user

def create_notification_for_users(title: str, message: str, user_ids: list):
     # Esta función crea una notificación y la asigna a varios usuarios.
    # Es llamada desde tasks.py para ejecutarse en background con Celery.

    # Creamos la notificación una sola vez con el título y mensaje.
    # Solo existe UN registro en la tabla Notification sin importar
    # cuántos usuarios la reciban.
    notification = Notification.objects.create(
        title=title,
        message=message
    )
    # Fan-out: creamos un registro NotificationUser por cada usuario.
    # bulk_create hace todo en UNA sola query a la base de datos,
    # en vez de hacer una query por cada usuario.
    # Si hay 1000 usuarios, sin bulk_create serían 1000 queries.
    # Con bulk_create es solo 1 query. Mucho más eficiente.
    NotificationUser.objects.bulk_create([
        NotificationUser(
            notification=notification,
            user_id=uid
        )
        for uid in user_ids
    ])

    return notification