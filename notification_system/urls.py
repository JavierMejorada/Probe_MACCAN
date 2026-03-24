from django.urls import path
from . import views

urlpatterns = [
     # GET /api/notifications/
    # Cuando alguien haga una petición GET a esta URL,
    # Django va a ejecutar la función NotificationListView
    # que regresa la lista de notificaciones del usuario autenticado.
     path(
        "",
        views.NotificationListView.as_view(),
        name="notification-list"
    ),
     # POST /api/notifications/<id>/read/
    # Cuando alguien haga una petición POST a esta URL,
    # Django va a ejecutar la función mark_as_read
    # que marca una notificación como leída.
    # El <int:notification_id> significa que espera un número entero
    # en la URL, por ejemplo: /api/notifications/5/read/
    path(
        "<int:notification_id>/read/",
        views.mark_as_read,
        name="notification-read"
    ),
]