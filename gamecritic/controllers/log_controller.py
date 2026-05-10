"""
controllers/log_controller.py
──────────────────────────────
Lógica de negocio para logs (MongoDB) y endpoints de administración.
"""

from datetime import datetime, timezone
from flask import request
from models import LogModel
from models.database import get_db


class LogController:

    @staticmethod
    def listar(id_usuario=None, accion=None, limit=50):
        docs = LogModel.get_all(id_usuario, accion, limit)
        return docs, 200

    @staticmethod
    def crear_manual(data: dict, payload: dict):
        if not data or 'accion' not in data:
            return {"error": "accion es obligatorio"}, 400

        data['id_usuario'] = int(payload['sub'])
        data['timestamp']  = datetime.now(timezone.utc)
        data['ip']         = request.remote_addr
        result = LogModel.insertar_manual(data)
        return {"message": "Log registrado", "id": str(result.inserted_id)}, 201


class AdminController:

    @staticmethod
    def listar_administradores():
        conn = get_db()
        rows = conn.execute('SELECT * FROM administrador').fetchall()
        conn.close()
        return [dict(r) for r in rows], 200

    @staticmethod
    def obtener_administrador(id_admin: int):
        conn = get_db()
        row = conn.execute(
            'SELECT * FROM administrador WHERE id_admin = ?', (id_admin,)
        ).fetchone()
        conn.close()
        if not row:
            return {"error": "Administrador no encontrado"}, 404
        return dict(row), 200

    @staticmethod
    def listar_personas():
        conn = get_db()
        rows = conn.execute('SELECT * FROM persona').fetchall()
        conn.close()
        return [dict(r) for r in rows], 200

    @staticmethod
    def obtener_persona(id_person: int, payload: dict):
        conn = get_db()
        persona = conn.execute(
            'SELECT * FROM persona WHERE id_person = ?', (id_person,)
        ).fetchone()
        conn.close()

        if not persona:
            return {"error": "Persona no encontrada"}, 404

        id_solicitante = int(payload['sub'])
        if payload['rol'] != 'admin' and persona['id_usuario'] != id_solicitante:
            return {"error": "No tienes permiso para ver este perfil"}, 403

        return dict(persona), 200
