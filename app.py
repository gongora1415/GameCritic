import sqlite3
import json


from flask import Flask, request, Response 

app = Flask(__name__)
DATABASE = 'database.db'

def jsonify(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        status=status,
        content_type='application/json; charset=utf-8'
    )

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    return conn

#  USUARIOS


@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM usuarios').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM usuarios WHERE id_usuario = ?', (id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(dict(row))

@app.route('/usuarios', methods=['POST'])
def create_usuario():
    data = request.get_json()
    if not data or not all(k in data for k in ('nombre', 'email', 'contraseña')):
        return jsonify({"error": "nombre, email y contraseña son obligatorios"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO usuarios (nombre, email, contraseña) VALUES (?, ?, ?)',
                   (data['nombre'], data['email'], data['contraseña']))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"id_usuario": new_id, **data}), 201

@app.route('/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usuarios WHERE id_usuario = ?', (id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify({"message": "Usuario eliminado"})

#  VIDEOJUEGOS


@app.route('/videojuegos', methods=['GET'])
def get_videojuegos():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM videojuegos ORDER BY id_juego DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/videojuegos/<int:id>', methods=['GET'])
def get_videojuego(id):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM videojuegos WHERE id_juego = ?', (id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Videojuego no encontrado"}), 404
    return jsonify(dict(row))

@app.route('/videojuegos', methods=['POST'])
def create_videojuego():
    data = request.get_json()
    if not data or not all(k in data for k in ('titulo', 'creado_por')):
        return jsonify({"error": "titulo y creado_por son obligatorios"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO videojuegos (titulo, descripcion, genero, fecha_de_lanzamiento, creado_por)
                      VALUES (?, ?, ?, ?, ?)''',
                   (data['titulo'], data.get('descripcion'), data.get('genero'),
                    data.get('fecha_de_lanzamiento'), data['creado_por']))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"id_juego": new_id, **data}), 201

@app.route('/videojuegos/<int:id>', methods=['PUT'])
def update_videojuego(id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''UPDATE videojuegos
                      SET titulo=?, descripcion=?, genero=?, fecha_de_lanzamiento=?
                      WHERE id_juego=?''',
                   (data.get('titulo'), data.get('descripcion'),
                    data.get('genero'), data.get('fecha_de_lanzamiento'), id))
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated == 0:
        return jsonify({"error": "Videojuego no encontrado"}), 404
    return jsonify({"message": "Videojuego actualizado"})

@app.route('/videojuegos/<int:id>', methods=['DELETE'])
def delete_videojuego(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM videojuegos WHERE id_juego = ?', (id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({"error": "Videojuego no encontrado"}), 404
    return jsonify({"message": "Videojuego eliminado"})

#  RESEÑAS


@app.route('/reseñas', methods=['GET'])
def get_reseñas():
    id_juego = request.args.get('id_juego')
    conn = get_db_connection()
    if id_juego:
        rows = conn.execute('SELECT * FROM reseñas WHERE id_juego = ?', (id_juego,)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM reseñas').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/reseñas', methods=['POST'])
def create_reseña():
    data = request.get_json()
    if not data or not all(k in data for k in ('contenido', 'id_usuario', 'id_juego')):
        return jsonify({"error": "contenido, id_usuario e id_juego son obligatorios"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO reseñas (contenido, id_usuario, id_juego) VALUES (?, ?, ?)',
                   (data['contenido'], data['id_usuario'], data['id_juego']))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"id_reseña": new_id, **data}), 201
@app.route('/reseñas/<int:id>', methods=['GET'])
def get_reseña(id):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM reseñas WHERE id_reseña = ?', (id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Reseña no encontrada"}), 404
    return jsonify(dict(row))
@app.route('/reseñas/<int:id>', methods=['DELETE'])
def delete_reseña(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM reseñas WHERE id_reseña = ?', (id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({"error": "Reseña no encontrada"}), 404
    return jsonify({"message": "Reseña eliminada"})

@app.route('/administradores', methods=['GET'])
def get_administradores():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM administrador').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/administradores/<int:id>', methods=['GET'])
def get_administrador(id):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM administrador WHERE id_admin = ?', (id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Administrador no encontrado"}), 404
    return jsonify(dict(row))

# PERSONA

@app.route('/personas', methods=['GET'])
def get_personas():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM persona').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/personas/<int:id>', methods=['GET'])
def get_persona(id):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM persona WHERE id_person = ?', (id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Persona no encontrada"}), 404
    return jsonify(dict(row))

#  CALIFICACIONES


@app.route('/calificaciones', methods=['GET'])
def get_calificaciones():
    id_juego = request.args.get('id_juego')
    conn = get_db_connection()
    if id_juego:
        rows = conn.execute('SELECT * FROM calificaciones WHERE id_juego = ?', (id_juego,)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM calificaciones').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])
@app.route('/calificaciones/<int:id>', methods=['GET'])
def get_calificacion(id):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM calificaciones WHERE id_calificacion = ?', (id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Calificación no encontrada"}), 404
    return jsonify(dict(row))
@app.route('/calificaciones', methods=['POST'])
def create_calificacion():
    data = request.get_json()
    if not data or not all(k in data for k in ('puntuacion', 'id_usuario', 'id_juego')):
        return jsonify({"error": "puntuacion, id_usuario e id_juego son obligatorios"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO calificaciones (puntuacion, id_usuario, id_juego) VALUES (?, ?, ?)',
                   (data['puntuacion'], data['id_usuario'], data['id_juego']))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"id_calificacion": new_id, **data}), 201

@app.route('/calificaciones/<int:id>', methods=['DELETE'])
def delete_calificacion(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM calificaciones WHERE id_calificacion = ?', (id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({"error": "Calificación no encontrada"}), 404
    return jsonify({"message": "Calificación eliminada"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)