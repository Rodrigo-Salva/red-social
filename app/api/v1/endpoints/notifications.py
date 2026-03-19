from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.notifications import manager
from app.api import deps
from jose import jwt
from app.core.config import settings
from app.schemas.token import TokenPayload

router = APIRouter()

import json

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    # En una app real, aquí validaríamos el token enviado en la query o headers
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Recibir datos del cliente
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                if payload.get("type") == "typing":
                    recipient_id = payload.get("recipient_id")
                    if recipient_id:
                        await manager.send_personal_message({
                            "type": "typing",
                            "from_id": client_id
                        }, user_id=recipient_id)
            except json.JSONDecodeError:
                pass # No es JSON, ignorar o manejar comandos de texto
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
