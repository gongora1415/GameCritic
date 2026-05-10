"""
controllers/resena_controller.py
─────────────────────────────────
Lógica de negocio para reseñas y calificaciones.
"""

import sqlite3
from models import ResenaModel, CalificacionModel, LogModel


class ResenaController:

    @staticmethod
    def listar(id_juego=None):
        return ResenaModel.get_all(id_juego), 200

    @staticmethod
    def obtener(id_resena: int):
        resena = ResenaModel.get_by_id(id_resena)
        if not resena:
            return {"error": "Reseña no encontrada"}, 404
        return resena, 200

    @staticmethod
    def crear(data: dict, payload: dict):
        if not data or not all(k in data for k in ('contenido', 'id_juego')):
            return {"error": "contenido e id_juego son obligatorios"}, 400

        id_usuario = int(payload['sub'])
        new_id = ResenaModel.create(data['contenido'], id_usuario, data['id_juego'])
        LogModel.registrar(id_usuario, "nueva_resena",
                           {"id_resena": new_id, "id_juego": data['id_juego']})
        return {"id_resena": new_id, "id_usuario": id_usuario, **data}, 201

    @staticmethod
    def eliminar(id_resena: int, payload: dict):
        resena = ResenaModel.get_by_id(id_resena)
        if not resena:
            return {"error": "Reseña no encontrada"}, 404

        id_solicitante = int(payload['sub'])
        if payload['rol'] != 'admin' and resena['id_usuario'] != id_solicitante:
            return {"error": "No tienes permiso para eliminar esta reseña"}, 403

        ResenaModel.delete(id_resena)
        LogModel.registrar(id_solicitante, "eliminacion_resena", {"id_resena": id_resena})
        return {"message": "Reseña eliminada"}, 200


class CalificacionController:

    @staticmethod
    def listar(id_juego=None):
        return CalificacionModel.get_all(id_juego), 200

    @staticmethod
    def obtener(id_calificacion: int):
        calificacion = CalificacionModel.get_by_id(id_calificacion)
        if not calificacion:
            return {"error": "Calificación no encontrada"}, 404
        return calificacion, 200

    @staticmethod
    def crear(data: dict, payload: dict):
        if not data or not all(k in data for k in ('puntuacion', 'id_juego')):
            return {"error": "puntuacion e id_juego son obligatorios"}, 400

        id_usuario = int(payload['sub'])
        try:
            new_id = CalificacionModel.create(
                data['puntuacion'], id_usuario, data['id_juego']
            )
        except sqlite3.IntegrityError as e:
            return {"error": f"Error de integridad: {e}"}, 400

        LogModel.registrar(id_usuario, "nueva_calificacion", {
            "id_calificacion": new_id,
            "puntuacion": data['puntuacion'],
            "id_juego": data['id_juego'],
        })
        return {"id_calificacion": new_id, "id_usuario": id_usuario, **data}, 201

    @staticmethod
    def eliminar(id_calificacion: int, payload: dict):
        calificacion = CalificacionModel.get_by_id(id_calificacion)
        if not calificacion:
            return {"error": "Calificación no encontrada"}, 404

        id_solicitante = int(payload['sub'])
        if payload['rol'] != 'admin' and calificacion['id_usuario'] != id_solicitante:
            return {"error": "No tienes permiso para eliminar esta calificación"}, 403

        CalificacionModel.delete(id_calificacion)
        LogModel.registrar(id_solicitante, "eliminacion_calificacion",
                           {"id_calificacion": id_calificacion})
        return {"message": "Calificación eliminada"}, 200
