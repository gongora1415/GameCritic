import sqlite3
# utf_8
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def setup_database():
    """Crea la base de datos con el esquema del modelo entidad-relación."""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # --- Tabla Usuarios ---
        print("Creando tabla 'usuarios'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario  INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre      TEXT NOT NULL,
                email       TEXT NOT NULL UNIQUE,
                contraseña  TEXT NOT NULL
            )
        ''')

        # --- Tabla Administrador ---
        print("Creando tabla 'administrador'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS administrador (
                id_admin     INTEGER PRIMARY KEY AUTOINCREMENT,
                estado       INTEGER NOT NULL DEFAULT 1,
                nivel_acceso INTEGER NOT NULL DEFAULT 1,
                id_usuario   INTEGER NOT NULL UNIQUE,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
            )
        ''')

        # --- Tabla Persona ---
        print("Creando tabla 'persona'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persona (
                id_person       INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_registro  TEXT NOT NULL DEFAULT CURRENT_DATE,
                nivel_acceso    INTEGER NOT NULL DEFAULT 0,
                edad            INTEGER,
                id_usuario      INTEGER NOT NULL UNIQUE,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
            )
        ''')

        # --- Tabla Videojuegos ---
        print("Creando tabla 'videojuegos'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videojuegos (
                id_juego             INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo               TEXT NOT NULL,
                descripcion          TEXT,
                genero               TEXT,
                fecha_de_lanzamiento TEXT,
                creado_por           INTEGER NOT NULL,
                FOREIGN KEY (creado_por) REFERENCES administrador(id_admin)
            )
        ''')

        # --- Tabla Reseñas ---
        print("Creando tabla 'reseñas'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reseñas (
                id_reseña  INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido  TEXT NOT NULL,
                fecha      TEXT NOT NULL DEFAULT CURRENT_DATE,
                id_usuario INTEGER NOT NULL,
                id_juego   INTEGER NOT NULL,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
                FOREIGN KEY (id_juego)   REFERENCES videojuegos(id_juego)
            )
        ''')

        # --- Tabla Calificaciones ---
        print("Creando tabla 'calificaciones'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calificaciones (
                id_calificacion INTEGER PRIMARY KEY AUTOINCREMENT,
                puntuacion      INTEGER NOT NULL CHECK(puntuacion BETWEEN 1 AND 10),
                id_usuario      INTEGER NOT NULL,
                id_juego        INTEGER NOT NULL,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
                FOREIGN KEY (id_juego)   REFERENCES videojuegos(id_juego)
            )
        ''')

        # ── Datos de prueba ──────────────────────────────────────────
        cursor.execute("INSERT INTO usuarios (nombre, email, contraseña) VALUES (?, ?, ?)",
                       ("Admin Root", "admin@games.com", "hashed_pass_1"))
        cursor.execute("INSERT INTO usuarios (nombre, email, contraseña) VALUES (?, ?, ?)",
                       ("Juan Gamer", "juan@games.com", "hashed_pass_2"))

        cursor.execute("INSERT INTO administrador (estado, nivel_acceso, id_usuario) VALUES (?, ?, ?)",
                       (1, 5, 1))

        cursor.execute("INSERT INTO persona (fecha_registro, nivel_acceso, edad, id_usuario) VALUES (?, ?, ?, ?)",
                       ("2024-01-15", 0, 22, 2))

        cursor.execute("""INSERT INTO videojuegos (titulo, descripcion, genero, fecha_de_lanzamiento, creado_por)
                          VALUES (?, ?, ?, ?, ?)""",
                       ("The Witcher 3", "RPG de mundo abierto", "RPG", "2015-05-19", 1))

        cursor.execute("""INSERT INTO reseñas (contenido, fecha, id_usuario, id_juego)
                          VALUES (?, ?, ?, ?)""",
                       ("Increible juego, historia magistral.", "2024-02-10", 2, 1))

        cursor.execute("INSERT INTO calificaciones (puntuacion, id_usuario, id_juego) VALUES (?, ?, ?)",
                       (10, 2, 1))

        conn.commit()
        print("✅ Base de datos inicializada con éxito.")

    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    setup_database()