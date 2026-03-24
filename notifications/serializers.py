# serializers.py
# Los serializers convierten los objetos de Python/Django
# a formato JSON para que la API pueda enviarlos,
# y también convierten JSON entrante a objetos de Python.
# Es como un traductor entre la base de datos y la API.

from rest_framework import serializers
from .models import Notification, NotificationUser


class NotificationSerializer(serializers.ModelSerializer):
    # Agregamos campos extra que no están directamente en Notification
    # sino en la tabla intermedia NotificationUser.
    # Son "calculados" dependiendo del usuario que hace la petición.
    is_read = serializers.SerializerMethodField()
    read_at = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ["id", "title", "message", "created_at", "is_read", "read_at"]

    def get_is_read(self, obj):
        # Obtenemos el estado de lectura para el usuario autenticado.
        # Cada usuario tiene su propio is_read en NotificationUser.
        user = self.context["request"].user
        try:
            status = obj.user_statuses.get(user=user)
            return status.is_read
        except Exception:
            return False

    def get_read_at(self, obj):
        # Igual que is_read, cada usuario tiene su propio read_at.
        user = self.context["request"].user
        try:
            status = obj.user_statuses.get(user=user)
            return status.read_at
        except Exception:
            return None