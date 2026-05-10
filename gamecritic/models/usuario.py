"""
models/usuario.py
─────────────────
Operaciones CRUD sobre la tabla `usuarios` en SQLite.
"""

from .database import get_db


class UsuarioModel:

    @staticmethod
    def get_all():
        conn = get_db()
        rows = conn.execute(
            'SELECT id_usuario, nombre, email FROM usuarios'
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(id_usuario: int):
        conn = get_db()
        row = conn.execute(
            'SELECT id_usuario, nombre, email FROM usuarios WHERE id_usuario = ?',
            (id_usuario,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_email(email: str):
        """Devuelve la fila completa (con contraseña) para autenticación."""
        conn = get_db()
        row = conn.execute(
            'SELECT * FROM usuarios WHERE email = ?',
            (email.strip().lower(),)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(nombre: str, email: str, contrasena_hash: str, edad=None):
        """
        Crea un usuario y su perfil de persona.
        Devuelve el id_usuario del nuevo registro.
        """
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO usuarios (nombre, email, contrasena) VALUES (?, ?, ?)',
            (nombre, email, contrasena_hash)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute(
            'INSERT INTO persona (id_usuario, edad) VALUES (?, ?)',
            (new_id, edad)
        )
        conn.commit()
        conn.close()
        return new_id

    @staticmethod
    def delete(id_usuario: int) -> bool:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM usuarios WHERE id_usuario = ?', (id_usuario,))
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        return deleted > 0

    @staticmethod
    def is_admin(id_usuario: int) -> bool:
        conn = get_db()
        row = conn.execute(
            'SELECT 1 FROM administrador WHERE id_usuario = ?', (id_usuario,)
        ).fetchone()
        conn.close()
        return row is not None

    @staticmethod
    def get_perfil_stats(id_usuario: int):
        conn = get_db()
        resenas = conn.execute(
            'SELECT * FROM resenas WHERE id_usuario = ?', (id_usuario,)
        ).fetchall()
        calificaciones = conn.execute(
            'SELECT * FROM calificaciones WHERE id_usuario = ?', (id_usuario,)
        ).fetchall()
        conn.close()
        return {
            "total_resenas": len(resenas),
            "total_calificaciones": len(calificaciones),
        }
