# tasks.py
# Las tareas de Celery son funciones que se ejecutan en segundo plano.
# Esto significa que cuando alguien crea una notificación para miles
# de usuarios, el servidor no se congela esperando a que termine.
# Celery lo hace en un proceso separado mientras el servidor sigue
# atendiendo otras peticiones.
#
# ¿Qué rol juega Redis aquí?
# Redis es el "mensajero" entre Django y Celery.
# Cuando llamamos a send_notification_to_users.delay(...), Django
# pone la tarea en una cola dentro de Redis.
# Celery está escuchando esa cola y cuando ve una tarea nueva la toma
# y la ejecuta. Sin Redis esta comunicación no sería posible.

from celery import shared_task
from django.contrib.auth.models import User
from .services import create_notification_for_users


@shared_task
def send_notification_to_users(title: str, message: str, user_ids: list):
    # Primero verificamos que los usuarios existen en la base de datos
    # para evitar errores al crear los registros NotificationUser.
    existing_ids = list(
        User.objects.filter(id__in=user_ids).values_list("id", flat=True)
    )

    if not existing_ids:
        return {"status": "no_valid_users", "count": 0}

    # Creamos la notificación y la distribuimos a todos los usuarios
    # usando bulk_create para hacer todo en una sola query.
    notification = create_notification_for_users(
        title=title,
        message=message,
        user_ids=existing_ids,
    )

    return {
        "status": "success",
        "notification_id": notification.id,
        "recipients_count": len(existing_ids),
    }