"""
models/videojuego.py
────────────────────
Operaciones CRUD sobre `videojuegos` (SQLite) y `metadata_juegos` (MongoDB).
"""

from datetime import datetime, timezone
from .database import get_db, metadata_col


class VideojuegoModel:

    # ── SQL ───────────────────────────────────────────────────

    @staticmethod
    def get_all():
        conn = get_db()
        rows = conn.execute(
            'SELECT * FROM videojuegos ORDER BY id_juego DESC'
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(id_juego: int):
        conn = get_db()
        row = conn.execute(
            'SELECT * FROM videojuegos WHERE id_juego = ?', (id_juego,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(titulo, descripcion, genero, fecha_lanzamiento, creado_por, imagen_url=None):
        conn = get_db()
        cursor = conn.cursor()
        # Agrega columna imagen_url si no existe (migración automática)
        try:
            cursor.execute('ALTER TABLE videojuegos ADD COLUMN imagen_url TEXT')
            conn.commit()
        except Exception:
            pass  # ya existe
        cursor.execute(
            '''INSERT INTO videojuegos
               (titulo, descripcion, genero, fecha_de_lanzamiento, creado_por, imagen_url)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (titulo, descripcion, genero, fecha_lanzamiento, creado_por, imagen_url)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    @staticmethod
    def update(id_juego, titulo, descripcion, genero, fecha_lanzamiento, imagen_url=None):
        conn = get_db()
        cursor = conn.cursor()
        # Agrega columna imagen_url si no existe (migración automática)
        try:
            cursor.execute('ALTER TABLE videojuegos ADD COLUMN imagen_url TEXT')
            conn.commit()
        except Exception:
            pass  # ya existe
        cursor.execute(
            '''UPDATE videojuegos
               SET titulo=?, descripcion=?, genero=?, fecha_de_lanzamiento=?, imagen_url=?
               WHERE id_juego=?''',
            (titulo, descripcion, genero, fecha_lanzamiento, imagen_url, id_juego)
        )
        conn.commit()
        updated = cursor.rowcount
        conn.close()
        return updated > 0

    @staticmethod
    def delete(id_juego: int) -> bool:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM videojuegos WHERE id_juego = ?', (id_juego,))
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        return deleted > 0

    # ── MongoDB metadata ──────────────────────────────────────

    @staticmethod
    def get_metadata(id_juego: int):
        return metadata_col.find_one({"id_juego": id_juego}, {"_id": 0}) or {}

    @staticmethod
    def upsert_metadata(id_juego: int, data: dict):
        data.update({"id_juego": id_juego, "creado_en": datetime.now(timezone.utc)})
        result = metadata_col.replace_one({"id_juego": id_juego}, data, upsert=True)
        return result.upserted_id is not None

    @staticmethod
    def patch_metadata(id_juego: int, data: dict):
        data['actualizado_en'] = datetime.now(timezone.utc)
        result = metadata_col.update_one({"id_juego": id_juego}, {"$set": data})
        return result.matched_count > 0

    @staticmethod
    def delete_metadata(id_juego: int) -> bool:
        result = metadata_col.delete_one({"id_juego": id_juego})
        return result.deleted_count > 0
