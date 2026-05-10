"""
controllers/videojuego_controller.py
─────────────────────────────────────
Lógica de negocio para videojuegos y su metadata.
"""

from models import VideojuegoModel, LogModel


class VideojuegoController:

    # ── CRUD SQL ──────────────────────────────────────────────

    @staticmethod
    def listar():
        return VideojuegoModel.get_all(), 200

    @staticmethod
    def obtener(id_juego: int):
        juego = VideojuegoModel.get_by_id(id_juego)
        if not juego:
            return {"error": "Videojuego no encontrado"}, 404
        return juego, 200

    @staticmethod
    def crear(data: dict, payload: dict):
        if not data or not all(k in data for k in ('titulo', 'creado_por')):
            return {"error": "titulo y creado_por son obligatorios"}, 400

        new_id = VideojuegoModel.create(
            data['titulo'],
            data.get('descripcion'),
            data.get('genero'),
            data.get('fecha_de_lanzamiento'),
            data['creado_por'],
            data.get('imagen_url'),
        )
        LogModel.registrar(int(payload['sub']), "creacion_juego",
                           {"id_juego": new_id, "titulo": data['titulo']})
        return {"id_juego": new_id, **data}, 201

    @staticmethod
    def actualizar(id_juego: int, data: dict, payload: dict):
        actualizado = VideojuegoModel.update(
            id_juego,
            data.get('titulo'),
            data.get('descripcion'),
            data.get('genero'),
            data.get('fecha_de_lanzamiento'),
            data.get('imagen_url'),
        )
        if not actualizado:
            return {"error": "Videojuego no encontrado"}, 404
        return {"message": "Videojuego actualizado"}, 200

    @staticmethod
    def eliminar(id_juego: int, payload: dict):
        eliminado = VideojuegoModel.delete(id_juego)
        if not eliminado:
            return {"error": "Videojuego no encontrado"}, 404
        LogModel.registrar(int(payload['sub']), "eliminacion_juego",
                           {"id_juego": id_juego})
        return {"message": "Videojuego eliminado"}, 200

    # ── Detalle combinado SQL + MongoDB ───────────────────────

    @staticmethod
    def detalle(id_juego: int):
        juego = VideojuegoModel.get_by_id(id_juego)
        if not juego:
            return {"error": "Videojuego no encontrado"}, 404
        metadata = VideojuegoModel.get_metadata(id_juego)
        return {"videojuego": juego, "metadata": metadata}, 200

    # ── Metadata MongoDB ──────────────────────────────────────

    @staticmethod
    def crear_metadata(id_juego: int, data: dict):
        if not data:
            return {"error": "Se requiere un cuerpo JSON"}, 400
        upserted = VideojuegoModel.upsert_metadata(id_juego, data)
        return {"id_juego": id_juego, "upserted": upserted}, 201

    @staticmethod
    def actualizar_metadata(id_juego: int, data: dict):
        if not data:
            return {"error": "Se requiere un cuerpo JSON"}, 400
        actualizado = VideojuegoModel.patch_metadata(id_juego, data)
        if not actualizado:
            return {"error": "Metadata no encontrada"}, 404
        return {"message": "Metadata actualizada"}, 200

    @staticmethod
    def eliminar_metadata(id_juego: int):
        eliminado = VideojuegoModel.delete_metadata(id_juego)
        if not eliminado:
            return {"error": "Metadata no encontrada"}, 404
        return {"message": "Metadata eliminada"}, 200
