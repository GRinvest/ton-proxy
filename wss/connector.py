from typing import List

from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, client: WebSocket):
        await client.accept()
        self.active_connections.append(client)

    async def disconnect(self, client: WebSocket):
        self.active_connections.remove(client)

    async def send_personal_message(self, message: str, client: WebSocket):
        await client.send_json(message)

    async def broadcast(self, msg):
        for connection in self.active_connections:
            await connection.send_json({"data": msg})
