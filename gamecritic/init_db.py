"""
init_db.py  —  Helpers bcrypt + setup de base de datos.
Importado por controllers/auth_controller.py para hash y verificación.
"""

import sqlite3
import sys
import io
import bcrypt

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BCRYPT_ROUNDS = 12


def hash_password(plain: str) -> str:
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verificar_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        plain.encode("utf-8"),
        hashed.encode("utf-8"),
    )


def setup_database():
    try:
        conn   = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario  INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL,
            email       TEXT NOT NULL UNIQUE,
            contrasena  TEXT NOT NULL
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS administrador (
            id_admin     INTEGER PRIMARY KEY AUTOINCREMENT,
            estado       INTEGER NOT NULL DEFAULT 1,
            nivel_acceso INTEGER NOT NULL DEFAULT 1,
            id_usuario   INTEGER NOT NULL UNIQUE,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS persona (
            id_person      INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_registro TEXT NOT NULL DEFAULT CURRENT_DATE,
            nivel_acceso   INTEGER NOT NULL DEFAULT 0,
            edad           INTEGER,
            id_usuario     INTEGER NOT NULL UNIQUE,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS videojuegos (
            id_juego             INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo               TEXT NOT NULL,
            descripcion          TEXT,
            genero               TEXT,
            fecha_de_lanzamiento TEXT,
            creado_por           INTEGER NOT NULL,
            FOREIGN KEY (creado_por) REFERENCES administrador(id_admin)
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS resenas (
            id_resena  INTEGER PRIMARY KEY AUTOINCREMENT,
            contenido  TEXT NOT NULL,
            fecha      TEXT NOT NULL DEFAULT CURRENT_DATE,
            id_usuario INTEGER NOT NULL,
            id_juego   INTEGER NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
            FOREIGN KEY (id_juego)   REFERENCES videojuegos(id_juego)
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS calificaciones (
            id_calificacion INTEGER PRIMARY KEY AUTOINCREMENT,
            puntuacion      INTEGER NOT NULL CHECK(puntuacion BETWEEN 1 AND 10),
            id_usuario      INTEGER NOT NULL,
            id_juego        INTEGER NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
            FOREIGN KEY (id_juego)   REFERENCES videojuegos(id_juego)
        )''')

        admin_hash = hash_password("admin123")
        juan_hash  = hash_password("juan456")

        cursor.execute(
            "INSERT OR IGNORE INTO usuarios (nombre, email, contrasena) VALUES (?, ?, ?)",
            ("Admin Root", "admin@games.com", admin_hash)
        )
        cursor.execute(
            "INSERT OR IGNORE INTO usuarios (nombre, email, contrasena) VALUES (?, ?, ?)",
            ("Juan Gamer", "juan@games.com", juan_hash)
        )
        cursor.execute(
            "INSERT OR IGNORE INTO administrador (estado, nivel_acceso, id_usuario) VALUES (?, ?, ?)",
            (1, 5, 1)
        )
        cursor.execute(
            "INSERT OR IGNORE INTO persona (fecha_registro, nivel_acceso, edad, id_usuario) VALUES (?, ?, ?, ?)",
            ("2024-01-15", 0, 22, 2)
        )
        cursor.execute(
            """INSERT OR IGNORE INTO videojuegos
               (titulo, descripcion, genero, fecha_de_lanzamiento, creado_por)
               VALUES (?, ?, ?, ?, ?)""",
            ("The Witcher 3", "RPG de mundo abierto", "RPG", "2015-05-19", 1)
        )
        cursor.execute(
            "INSERT OR IGNORE INTO resenas (contenido, fecha, id_usuario, id_juego) VALUES (?, ?, ?, ?)",
            ("Increíble juego, historia magistral.", "2024-02-10", 2, 1)
        )
        cursor.execute(
            "INSERT OR IGNORE INTO calificaciones (puntuacion, id_usuario, id_juego) VALUES (?, ?, ?)",
            (10, 2, 1)
        )

        conn.commit()
        print("Base de datos inicializada.")
        print("  admin@games.com / admin123")
        print("  juan@games.com  / juan456")
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    setup_database()
