from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.notifications import manager
from app.api import deps
from jose import jwt
from app.core.config import settings
from app.schemas.token import TokenPayload

router = APIRouter()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    # En una app real, aquí validaríamos el token enviado en la query o headers
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Mantener conexión abierta
            data = await websocket.receive_text()
            # Podríamos manejar comandos desde el cliente aquí si fuera necesario
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
