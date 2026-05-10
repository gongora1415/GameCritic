"""
models/log.py
─────────────
Acceso a la colección `logs_actividad` en MongoDB.
"""

from datetime import datetime, timezone
from pymongo import DESCENDING
from flask import request
from .database import logs_col


class LogModel:

    @staticmethod
    def registrar(id_usuario: int, accion: str, detalles: dict = None):
        """Inserta un documento de log con timestamp UTC e IP del cliente."""
        logs_col.insert_one({
            "id_usuario": id_usuario,
            "accion":     accion,
            "detalles":   detalles or {},
            "timestamp":  datetime.now(timezone.utc),
            "ip":         request.remote_addr,
        })

    @staticmethod
    def get_all(id_usuario=None, accion=None, limit=50):
        filtro = {}
        if id_usuario:
            filtro['id_usuario'] = int(id_usuario)
        if accion:
            filtro['accion'] = accion
        return list(
            logs_col.find(filtro, {"_id": 0})
                    .sort("timestamp", DESCENDING)
                    .limit(limit)
        )

    @staticmethod
    def get_recientes(id_usuario: int, limit=10):
        return list(
            logs_col.find({"id_usuario": id_usuario}, {"_id": 0})
                    .sort("timestamp", DESCENDING)
                    .limit(limit)
        )

    @staticmethod
    def insertar_manual(data: dict):
        return logs_col.insert_one(data)
