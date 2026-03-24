# views.py
# Las views reciben las peticiones HTTP y regresan respuestas.
# Aquí definimos qué pasa cuando alguien llama a cada endpoint.
# La lógica pesada la delegamos a services.py para mantener esto limpio.

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer
from .services import mark_notification_as_read


class NotificationListView(generics.ListAPIView):
    # GET /api/notifications/
    # Lista todas las notificaciones del usuario autenticado.
    #
    # OPTIMIZACIÓN N+1:
    # Sin prefetch_related, por cada notificación se haría una query
    # extra para obtener el NotificationUser del usuario actual.
    # Si hay 100 notificaciones = 101 queries en total.
    # Con prefetch_related('user_statuses') = solo 2 queries en total.
    # Esto es muy importante para no matar el servidor con muchos usuarios.

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            Notification.objects.filter(
                user_statuses__user=user,
                is_deleted=False,
            )
            # prefetch_related trae todos los user_statuses en una
            # sola query adicional en vez de una por cada notificación
            .prefetch_related("user_statuses")
            .order_by("-created_at")
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_as_read(request, notification_id):
    # POST /api/notifications/<id>/read/
    # Marca una notificación como leída para el usuario autenticado.
    # Delega la lógica al servicio para mantener la view limpia.
    notification_user = mark_notification_as_read(
        user_id=request.user.id,
        notification_id=notification_id,
    )
    return Response(
        {
            "detail": "Notificación marcada como leída.",
            "read_at": notification_user.read_at,
        },
        status=status.HTTP_200_OK,
    )