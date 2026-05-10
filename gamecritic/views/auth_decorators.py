"""
views/auth_decorators.py
─────────────────────────
Decoradores que protegen rutas verificando el JWT en el header.
Pertenecen a la capa de Vista porque deciden QUÉ respuesta HTTP
se envía antes de llegar al controlador.
"""

from functools import wraps
from flask import request
from models import TokenModel
from .json_view import json_response


def _obtener_payload() -> dict | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    return TokenModel.validar(token)


def token_required(f):
    """Requiere JWT válido. Inyecta `payload` como primer argumento."""
    @wraps(f)
    def decorated(*args, **kwargs):
        payload = _obtener_payload()
        if payload is None:
            return json_response(
                {"error": "Token inválido o expirado. Inicia sesión."}, 401
            )
        return f(payload, *args, **kwargs)
    return decorated


def admin_required(f):
    """Requiere JWT válido con rol 'admin'."""
    @wraps(f)
    def decorated(*args, **kwargs):
        payload = _obtener_payload()
        if payload is None:
            return json_response(
                {"error": "Token inválido o expirado. Inicia sesión."}, 401
            )
        if payload.get("rol") != "admin":
            return json_response(
                {"error": "Acceso denegado: se requiere rol de administrador."}, 403
            )
        return f(payload, *args, **kwargs)
    return decorated
