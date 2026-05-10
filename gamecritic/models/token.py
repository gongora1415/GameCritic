"""
models/token.py
───────────────
Persistencia y revocación de JWT en MongoDB.
"""

import uuid
import jwt as pyjwt
from datetime import datetime, timezone, timedelta
from .database import tokens_col

SECRET_KEY      = "clave_super_secreta_cambiar_en_produccion"
ALGORITHM       = "HS256"
TOKEN_EXP_HOURS = 2


class TokenModel:

    @staticmethod
    def generar(id_usuario: int, email: str, rol: str) -> str:
        """
        Genera un JWT firmado HS256 y persiste el JTI en MongoDB.
        El índice TTL elimina automáticamente el documento al expirar.
        """
        ahora  = datetime.now(timezone.utc)
        expira = ahora + timedelta(hours=TOKEN_EXP_HOURS)
        jti    = str(uuid.uuid4())

        payload = {
            "jti":   jti,
            "sub":   str(id_usuario),
            "email": email,
            "rol":   rol,
            "iat":   int(ahora.timestamp()),
            "exp":   int(expira.timestamp()),
        }
        token = pyjwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        tokens_col.insert_one({
            "jti":        jti,
            "id_usuario": id_usuario,
            "email":      email,
            "rol":        rol,
            "emitido_en": ahora,
            "expira_en":  expira,
            "revocado":   False,
        })
        return token

    @staticmethod
    def validar(token: str) -> dict | None:
        """
        Decodifica el JWT y verifica que el JTI exista y no esté revocado.
        Devuelve el payload o None si el token no es válido.
        """
        try:
            payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except pyjwt.PyJWTError:
            return None

        jti = payload.get("jti")
        if not jti:
            return None

        doc = tokens_col.find_one({"jti": jti})
        if doc is None or doc.get("revocado"):
            return None

        return payload

    @staticmethod
    def revocar(jti: str):
        """Marca el JTI como revocado (logout inmediato)."""
        tokens_col.update_one({"jti": jti}, {"$set": {"revocado": True}})

    @staticmethod
    def expira_en() -> str:
        return (datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXP_HOURS)).isoformat()
