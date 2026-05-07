import os
from fastapi import Request, HTTPException
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware

_API_KEY = os.getenv("API_KEY", "")

# Rutas que no requieren autenticación
_PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        if not _API_KEY:
            # Sin API_KEY configurada, se permite todo (modo desarrollo)
            return await call_next(request)

        key = request.headers.get("X-API-Key", "")
        if key != _API_KEY:
            raise HTTPException(status_code=401, detail="API key inválida o ausente")

        return await call_next(request)
