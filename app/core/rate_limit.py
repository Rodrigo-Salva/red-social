import time
from fastapi import HTTPException, Request, status
from typing import Dict, Tuple

# Un limitador de velocidad muy simple en memoria. 
# En producción se usaría Redis.
class RateLimiter:
    def __init__(self, requests_limit: int, window_seconds: int):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.clients: Dict[str, List[float]] = {}

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        if client_id not in self.clients:
            self.clients[client_id] = [now]
            return True
        
        # Eliminar timestamps fuera de la ventana
        self.clients[client_id] = [t for t in self.clients[client_id] if now - t < self.window_seconds]
        
        if len(self.clients[client_id]) < self.requests_limit:
            self.clients[client_id].append(now)
            return True
        
        return False

# Limitadores específicos
login_limiter = RateLimiter(requests_limit=5, window_seconds=60) # 5 intentos por minuto
report_limiter = RateLimiter(requests_limit=10, window_seconds=3600) # 10 reportes por hora

async def rate_limit_login(request: Request):
    client_ip = request.client.host
    if not login_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos. Por favor, espera un minuto."
        )

async def rate_limit_reports(request: Request):
    client_ip = request.client.host
    if not report_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Has enviado demasiados reportes. Inténtalo más tarde."
        )
