# consumers.py
# Los consumers son como las "views" pero para WebSockets.
# Mientras que una view atiende una petición y termina,
# un consumer mantiene una conexión abierta con el cliente
# para poder enviarle mensajes en cualquier momento.
#
# ¿Qué rol juega Redis aquí?
# Django Channels usa Redis como "channel layer", que es el sistema
# que permite comunicar diferentes workers del servidor entre sí.
# Sin Redis, si tienes dos servidores corriendo, un usuario conectado
# al Servidor A nunca recibiría notificaciones creadas en el Servidor B.
# Redis actúa como el intermediario que conecta todo.
#
# Flujo completo:
# 1. Usuario abre el navegador → se conecta por WebSocket aquí
# 2. Se une al grupo "user_<su_id>" en Redis
# 3. Cuando se crea una notificación para él, alguien hace group_send
# 4. Redis distribuye el mensaje a este consumer
# 5. El usuario recibe la notificación sin recargar la página

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Se ejecuta cuando el cliente abre la conexión WebSocket.
        self.user = self.scope["user"]

        # Si el usuario no está autenticado cerramos la conexión.
        if not self.user.is_authenticated:
            await self.close()
            return

        # Cada usuario tiene su propio grupo en Redis.
        # Formato: "user_42" para el usuario con ID 42.
        self.group_name = f"user_{self.user.id}"

        # Unimos esta conexión al grupo del usuario en Redis.
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        # Confirmamos la conexión al cliente.
        await self.accept()

    async def disconnect(self, close_code):
        # Se ejecuta cuando el cliente cierra la conexión.
        # Salimos del grupo para no seguir recibiendo mensajes.
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def receive(self, text_data):
        # Se ejecuta cuando el cliente nos envía algo.
        # En este sistema los clientes no envían mensajes,
        # solo los reciben, entonces no hacemos nada aquí.
        pass

    async def notification_message(self, event):
        # Se ejecuta cuando alguien hace group_send con
        # type="notification_message" al grupo de este usuario.
        # Reenviamos el mensaje al cliente por WebSocket.
        await self.send(text_data=json.dumps({
            "type": "new_notification",
            "title": event["title"],
            "message": event["message"],
            "notification_id": event["notification_id"],
        }))