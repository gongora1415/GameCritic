from flask import Flask, request, Response
from pymongo import MongoClient , DESCENDING
import sqlite3, json, os
from datetime import datetime, timezone
from bson import ObjectId

client = MongoClient("mongodb+srv://admin:admin@cluster0.jw471dd.mongodb.net/?appName=Cluster0")
db = client['gamecritic']
logs_col = db['logs_actividad']
metadata_col = db['metadata_juegos']

app = Flask(__name__)
DATABASE = 'database.db'

# ── Helpers ──────────────────────────────────────────────────────────────────

def jsonify(data, status=200):
    """Serializa a JSON con soporte UTF-8 y ObjectId de Mongo."""
    def default(obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    return Response(
        json.dumps(data, ensure_ascii=False, indent=2, default=default),
        status=status,
        content_type='application/json; charset=utf-8'
    )


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def registrar_log(id_usuario, accion, detalles=None):
    """Inserta un documento de log en MongoDB."""
    logs_col.insert_one({
        "id_usuario": id_usuario,
        "accion": accion,
        "detalles": detalles or {},
        "timestamp": datetime.now(timezone.utc),
        "ip": request.remote_addr
    })


# ════════════════════════════════════════════════════════════════════════════
#  USUARIOS  (SQL)
# ════════════════════════════════════════════════════════════════════════════

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
    registrar_log(id, "consulta_usuario", {"id_usuario_consultado": id})
    return jsonify(dict(row))


@app.route('/usuarios', methods=['POST'])
def create_usuario():
    data = request.get_json()
    if not data or not all(k in data for k in ('nombre', 'email', 'contraseña')):
        return jsonify({"error": "nombre, email y contraseña son obligatorios"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO usuarios (nombre, email, contraseña) VALUES (?, ?, ?)',
        (data['nombre'], data['email'], data['contraseña'])
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    registrar_log(new_id, "registro_usuario", {"nombre": data['nombre'], "email": data['email']})
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
    registrar_log(id, "eliminacion_usuario")
    return jsonify({"message": "Usuario eliminado"})


# ── Endpoint combinado SQL + NoSQL ───────────────────────────────────────────

@app.route('/usuarios/<int:id>/perfil', methods=['GET'])
def get_perfil_usuario(id):
    """
    Combina datos estructurados (SQL) con historial de actividad (MongoDB).
    Devuelve el perfil completo del usuario + sus últimas 10 acciones.
    """
    conn = get_db_connection()
    usuario = conn.execute('SELECT * FROM usuarios WHERE id_usuario = ?', (id,)).fetchone()

    if usuario is None:
        conn.close()
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Datos relacionales: reseñas y calificaciones del usuario
    reseñas = conn.execute(
        'SELECT * FROM reseñas WHERE id_usuario = ?', (id,)
    ).fetchall()
    calificaciones = conn.execute(
        'SELECT * FROM calificaciones WHERE id_usuario = ?', (id,)
    ).fetchall()
    conn.close()

    # Últimas 10 actividades desde MongoDB
    ultimos_logs = list(
        logs_col.find({"id_usuario": id}, {"_id": 0})
                .sort("timestamp", DESCENDING)
                .limit(10)
    )

    perfil = {
        "usuario": dict(usuario),
        "estadisticas": {
            "total_reseñas": len(reseñas),
            "total_calificaciones": len(calificaciones)
        },
        "ultimas_actividades": ultimos_logs
    }
    registrar_log(id, "consulta_perfil")
    return jsonify(perfil)


# ════════════════════════════════════════════════════════════════════════════
#  VIDEOJUEGOS  (SQL)
# ════════════════════════════════════════════════════════════════════════════

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
    cursor.execute(
        '''INSERT INTO videojuegos (titulo, descripcion, genero, fecha_de_lanzamiento, creado_por)
           VALUES (?, ?, ?, ?, ?)''',
        (data['titulo'], data.get('descripcion'), data.get('genero'),
         data.get('fecha_de_lanzamiento'), data['creado_por'])
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    registrar_log(data['creado_por'], "creacion_juego", {"id_juego": new_id, "titulo": data['titulo']})
    return jsonify({"id_juego": new_id, **data}), 201


@app.route('/videojuegos/<int:id>', methods=['PUT'])
def update_videojuego(id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE videojuegos
           SET titulo=?, descripcion=?, genero=?, fecha_de_lanzamiento=?
           WHERE id_juego=?''',
        (data.get('titulo'), data.get('descripcion'),
         data.get('genero'), data.get('fecha_de_lanzamiento'), id)
    )
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


# ── Endpoint combinado: juego + metadata dinámica ────────────────────────────

@app.route('/videojuegos/<int:id>/detalle', methods=['GET'])
def get_detalle_juego(id):
    """
    Combina datos del juego (SQL) con metadata dinámica de MongoDB:
    requisitos del sistema, plataformas, idiomas, DLCs, etc.
    """
    conn = get_db_connection()
    juego = conn.execute('SELECT * FROM videojuegos WHERE id_juego = ?', (id,)).fetchone()
    reseñas = conn.execute(
        'SELECT contenido, fecha FROM reseñas WHERE id_juego = ?', (id,)
    ).fetchall()
    calificaciones = conn.execute(
        'SELECT puntuacion FROM calificaciones WHERE id_juego = ?', (id,)
    ).fetchall()
    conn.close()

    if juego is None:
        return jsonify({"error": "Videojuego no encontrado"}), 404

    puntuaciones = [c['puntuacion'] for c in calificaciones]
    promedio = round(sum(puntuaciones) / len(puntuaciones), 2) if puntuaciones else None

    # Metadata dinámica desde MongoDB
    metadata = metadata_col.find_one({"id_juego": id}, {"_id": 0})

    detalle = {
        "juego": dict(juego),
        "calificacion_promedio": promedio,
        "total_reseñas": len(reseñas),
        "reseñas_recientes": [dict(r) for r in reseñas[:5]],
        "metadata_dinamica": metadata or {}
    }
    return jsonify(detalle)


# ════════════════════════════════════════════════════════════════════════════
#  METADATA DINÁMICA DE JUEGOS  (NoSQL - MongoDB)
# ════════════════════════════════════════════════════════════════════════════

@app.route('/videojuegos/<int:id>/metadata', methods=['GET'])
def get_metadata_juego(id):
    """Recupera la metadata dinámica de un juego desde MongoDB."""
    doc = metadata_col.find_one({"id_juego": id}, {"_id": 0})
    if doc is None:
        return jsonify({"error": "Metadata no encontrada"}), 404
    return jsonify(doc)


@app.route('/videojuegos/<int:id>/metadata', methods=['POST'])
def create_metadata_juego(id):
    """
    Crea metadata dinámica para un juego (plataformas, requisitos, DLCs, idiomas...).
    Acepta cualquier campo adicional sin restricciones de esquema.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Se requiere un cuerpo JSON"}), 400

    # Verificar que el juego existe en SQL
    conn = get_db_connection()
    juego = conn.execute('SELECT id_juego FROM videojuegos WHERE id_juego = ?', (id,)).fetchone()
    conn.close()
    if juego is None:
        return jsonify({"error": "Videojuego no encontrado en SQL"}), 404

    data['id_juego'] = id
    data['actualizado_en'] = datetime.now(timezone.utc)

    result = metadata_col.replace_one({"id_juego": id}, data, upsert=True)
    return jsonify({
        "message": "Metadata guardada",
        "id_juego": id,
        "upserted": result.upserted_id is not None
    }), 201


@app.route('/videojuegos/<int:id>/metadata', methods=['PUT'])
def update_metadata_juego(id):
    """Actualiza campos específicos de la metadata sin reemplazar el documento completo."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Se requiere un cuerpo JSON"}), 400

    data['actualizado_en'] = datetime.now(timezone.utc)
    result = metadata_col.update_one({"id_juego": id}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "Metadata no encontrada"}), 404
    return jsonify({"message": "Metadata actualizada"})


@app.route('/videojuegos/<int:id>/metadata', methods=['DELETE'])
def delete_metadata_juego(id):
    """Elimina la metadata dinámica de un juego."""
    result = metadata_col.delete_one({"id_juego": id})
    if result.deleted_count == 0:
        return jsonify({"error": "Metadata no encontrada"}), 404
    return jsonify({"message": "Metadata eliminada"})


# ════════════════════════════════════════════════════════════════════════════
#  LOGS DE ACTIVIDAD  (NoSQL - MongoDB)
# ════════════════════════════════════════════════════════════════════════════

@app.route('/logs', methods=['GET'])
def get_logs():
    """Lista logs de actividad con filtros opcionales por usuario y acción."""
    filtro = {}
    id_usuario = request.args.get('id_usuario')
    accion = request.args.get('accion')
    limit = int(request.args.get('limit', 50))

    if id_usuario:
        filtro['id_usuario'] = int(id_usuario)
    if accion:
        filtro['accion'] = accion

    docs = list(
        logs_col.find(filtro, {"_id": 0})
                .sort("timestamp", DESCENDING)
                .limit(limit)
    )
    return jsonify(docs)


@app.route('/logs', methods=['POST'])
def create_log_manual():
    """Inserta un log manualmente (útil para eventos desde el cliente)."""
    data = request.get_json()
    if not data or not all(k in data for k in ('id_usuario', 'accion')):
        return jsonify({"error": "id_usuario y accion son obligatorios"}), 400
    data['timestamp'] = datetime.now(timezone.utc)
    data['ip'] = request.remote_addr
    result = logs_col.insert_one(data)
    return jsonify({"message": "Log registrado", "id": str(result.inserted_id)}), 201


# ════════════════════════════════════════════════════════════════════════════
#  RESEÑAS  (SQL)
# ════════════════════════════════════════════════════════════════════════════

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


@app.route('/reseñas/<int:id>', methods=['GET'])
def get_reseña(id):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM reseñas WHERE id_reseña = ?', (id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Reseña no encontrada"}), 404
    return jsonify(dict(row))


@app.route('/reseñas', methods=['POST'])
def create_reseña():
    data = request.get_json()
    if not data or not all(k in data for k in ('contenido', 'id_usuario', 'id_juego')):
        return jsonify({"error": "contenido, id_usuario e id_juego son obligatorios"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO reseñas (contenido, id_usuario, id_juego) VALUES (?, ?, ?)',
        (data['contenido'], data['id_usuario'], data['id_juego'])
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    registrar_log(data['id_usuario'], "nueva_reseña",
                  {"id_reseña": new_id, "id_juego": data['id_juego']})
    return jsonify({"id_reseña": new_id, **data}), 201


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


# ════════════════════════════════════════════════════════════════════════════
#  CALIFICACIONES  (SQL)
# ════════════════════════════════════════════════════════════════════════════

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
    cursor.execute(
        'INSERT INTO calificaciones (puntuacion, id_usuario, id_juego) VALUES (?, ?, ?)',
        (data['puntuacion'], data['id_usuario'], data['id_juego'])
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    registrar_log(data['id_usuario'], "nueva_calificacion",
                  {"id_calificacion": new_id, "puntuacion": data['puntuacion'],
                   "id_juego": data['id_juego']})
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


# ════════════════════════════════════════════════════════════════════════════
#  ADMINISTRADORES / PERSONAS  (SQL)
# ════════════════════════════════════════════════════════════════════════════

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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
