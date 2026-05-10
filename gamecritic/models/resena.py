"""
models/resena.py  /  models/calificacion.py
────────────────────────────────────────────
Ambos modelos en un solo módulo para mantener el proyecto compacto.
"""

from .database import get_db


# ══════════════════════════════════════════════════════════════
# ResenaModel
# ══════════════════════════════════════════════════════════════

class ResenaModel:

    @staticmethod
    def get_all(id_juego=None):
        conn = get_db()
        if id_juego:
            rows = conn.execute(
                'SELECT * FROM resenas WHERE id_juego = ?', (id_juego,)
            ).fetchall()
        else:
            rows = conn.execute('SELECT * FROM resenas').fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(id_resena: int):
        conn = get_db()
        row = conn.execute(
            'SELECT * FROM resenas WHERE id_resena = ?', (id_resena,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(contenido: str, id_usuario: int, id_juego: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO resenas (contenido, id_usuario, id_juego) VALUES (?, ?, ?)',
            (contenido, id_usuario, id_juego)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    @staticmethod
    def delete(id_resena: int) -> bool:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM resenas WHERE id_resena = ?', (id_resena,))
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        return deleted > 0


# ══════════════════════════════════════════════════════════════
# CalificacionModel
# ══════════════════════════════════════════════════════════════

class CalificacionModel:

    @staticmethod
    def get_all(id_juego=None):
        conn = get_db()
        if id_juego:
            rows = conn.execute(
                'SELECT * FROM calificaciones WHERE id_juego = ?', (id_juego,)
            ).fetchall()
        else:
            rows = conn.execute('SELECT * FROM calificaciones').fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(id_calificacion: int):
        conn = get_db()
        row = conn.execute(
            'SELECT * FROM calificaciones WHERE id_calificacion = ?', (id_calificacion,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(puntuacion: int, id_usuario: int, id_juego: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO calificaciones (puntuacion, id_usuario, id_juego) VALUES (?, ?, ?)',
            (puntuacion, id_usuario, id_juego)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    @staticmethod
    def delete(id_calificacion: int) -> bool:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM calificaciones WHERE id_calificacion = ?', (id_calificacion,)
        )
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        return deleted > 0
