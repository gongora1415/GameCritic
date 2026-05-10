"""
controllers/usuario_controller.py
──────────────────────────────────
Lógica de negocio para gestión de usuarios y perfiles.
"""

from models import UsuarioModel, LogModel
from pymongo import DESCENDING
from models.database import logs_col


class UsuarioController:

    @staticmethod
    def listar():
        return UsuarioModel.get_all(), 200

    @staticmethod
    def obtener(id_usuario: int, payload: dict):
        id_solicitante = int(payload['sub'])
        if payload['rol'] != 'admin' and id_solicitante != id_usuario:
            return {"error": "No tienes permiso para ver este usuario"}, 403

        usuario = UsuarioModel.get_by_id(id_usuario)
        if not usuario:
            return {"error": "Usuario no encontrado"}, 404

        LogModel.registrar(id_solicitante, "consulta_usuario",
                           {"id_usuario_consultado": id_usuario})
        return usuario, 200

    @staticmethod
    def eliminar(id_usuario: int, payload: dict):
        eliminado = UsuarioModel.delete(id_usuario)
        if not eliminado:
            return {"error": "Usuario no encontrado"}, 404
        LogModel.registrar(int(payload['sub']), "eliminacion_usuario",
                           {"id_eliminado": id_usuario})
        return {"message": "Usuario eliminado"}, 200

    @staticmethod
    def perfil(id_usuario: int, payload: dict):
        id_solicitante = int(payload['sub'])
        if payload['rol'] != 'admin' and id_solicitante != id_usuario:
            return {"error": "No tienes permiso para ver este perfil"}, 403

        usuario = UsuarioModel.get_by_id(id_usuario)
        if not usuario:
            return {"error": "Usuario no encontrado"}, 404

        stats        = UsuarioModel.get_perfil_stats(id_usuario)
        ultimos_logs = LogModel.get_recientes(id_usuario)

        LogModel.registrar(id_solicitante, "consulta_perfil", {"id_perfil": id_usuario})
        return {
            "usuario":          usuario,
            "estadisticas":     stats,
            "ultimas_actividades": ultimos_logs,
        }, 200
