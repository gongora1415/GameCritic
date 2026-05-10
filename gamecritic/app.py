"""
app.py  —  Punto de entrada de GameCritic
══════════════════════════════════════════
Arquitectura MVC:
  • Models      → models/          (acceso a datos: SQLite + MongoDB)
  • Controllers → controllers/     (lógica de negocio)
  • Views       → views/           (respuesta HTTP: JSON + decoradores auth)
                  views/templates/ (frontend HTML)
                  static/          (CSS + JS)

Cada ruta:
  1. Extrae parámetros del request  (responsabilidad de la Vista/ruta)
  2. Llama al Controlador           (lógica de negocio)
  3. Devuelve json_response(...)    (serialización → Vista)
"""

from flask import Flask, request, send_from_directory

# ── Vistas ────────────────────────────────────────
from views.json_view       import json_response
from views.auth_decorators import token_required, admin_required

# ── Controladores ─────────────────────────────────
from controllers import (
    AuthController,
    UsuarioController,
    VideojuegoController,
    ResenaController,
    CalificacionController,
    LogController,
    AdminController,
)

# ─────────────────────────────────────────────────
app = Flask(__name__,
            template_folder='views/templates',
            static_folder='static')


# ══════════════════════════════════════════════════
# FRONTEND  — sirve el SPA
# ══════════════════════════════════════════════════

@app.route('/')
def index():
    return send_from_directory('views/templates', 'index.html')


# ══════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════

@app.route('/auth/registro', methods=['POST'])
def registro():
    d = request.get_json() or {}
    if not all(k in d for k in ('nombre', 'email', 'contrasena')):
        return json_response({"error": "nombre, email y contraseña son obligatorios"}, 400)
    data, status = AuthController.registro(
        d['nombre'], d['email'], d['contrasena'], d.get('edad')
    )
    return json_response(data, status)


@app.route('/auth/login', methods=['POST'])
def login():
    d = request.get_json() or {}
    if not all(k in d for k in ('email', 'contrasena')):
        return json_response({"error": "email y contraseña son obligatorios"}, 400)
    data, status = AuthController.login(d['email'], d['contrasena'])
    return json_response(data, status)


@app.route('/auth/logout', methods=['POST'])
@token_required
def logout(payload):
    data, status = AuthController.logout(payload)
    return json_response(data, status)


# ══════════════════════════════════════════════════
# USUARIOS
# ══════════════════════════════════════════════════

@app.route('/usuarios', methods=['GET'])
@admin_required
def get_usuarios(payload):
    data, status = UsuarioController.listar()
    return json_response(data, status)


@app.route('/usuarios/<int:id>', methods=['GET'])
@token_required
def get_usuario(payload, id):
    data, status = UsuarioController.obtener(id, payload)
    return json_response(data, status)


@app.route('/usuarios/<int:id>', methods=['DELETE'])
@admin_required
def delete_usuario(payload, id):
    data, status = UsuarioController.eliminar(id, payload)
    return json_response(data, status)


@app.route('/usuarios/<int:id>/perfil', methods=['GET'])
@token_required
def get_perfil(payload, id):
    data, status = UsuarioController.perfil(id, payload)
    return json_response(data, status)


# ══════════════════════════════════════════════════
# VIDEOJUEGOS
# ══════════════════════════════════════════════════

@app.route('/videojuegos', methods=['GET'])
def get_videojuegos():
    data, status = VideojuegoController.listar()
    return json_response(data, status)


@app.route('/videojuegos/<int:id>', methods=['GET'])
def get_videojuego(id):
    data, status = VideojuegoController.obtener(id)
    return json_response(data, status)


@app.route('/videojuegos', methods=['POST'])
@admin_required
def create_videojuego(payload):
    data, status = VideojuegoController.crear(request.get_json(), payload)
    return json_response(data, status)


@app.route('/videojuegos/<int:id>', methods=['PUT'])
@admin_required
def update_videojuego(payload, id):
    data, status = VideojuegoController.actualizar(id, request.get_json() or {}, payload)
    return json_response(data, status)


@app.route('/videojuegos/<int:id>', methods=['DELETE'])
@admin_required
def delete_videojuego(payload, id):
    data, status = VideojuegoController.eliminar(id, payload)
    return json_response(data, status)


@app.route('/videojuegos/<int:id>/detalle', methods=['GET'])
def get_detalle_juego(id):
    data, status = VideojuegoController.detalle(id)
    return json_response(data, status)


@app.route('/videojuegos/<int:id>/metadata', methods=['POST'])
@admin_required
def create_metadata(payload, id):
    data, status = VideojuegoController.crear_metadata(id, request.get_json())
    return json_response(data, status)


@app.route('/videojuegos/<int:id>/metadata', methods=['PUT'])
@admin_required
def update_metadata(payload, id):
    data, status = VideojuegoController.actualizar_metadata(id, request.get_json())
    return json_response(data, status)


@app.route('/videojuegos/<int:id>/metadata', methods=['DELETE'])
@admin_required
def delete_metadata(payload, id):
    data, status = VideojuegoController.eliminar_metadata(id)
    return json_response(data, status)


# ══════════════════════════════════════════════════
# RESEÑAS
# ══════════════════════════════════════════════════

@app.route('/resenas', methods=['GET'])
def get_resenas():
    data, status = ResenaController.listar(request.args.get('id_juego'))
    return json_response(data, status)


@app.route('/resenas/<int:id>', methods=['GET'])
def get_resena(id):
    data, status = ResenaController.obtener(id)
    return json_response(data, status)


@app.route('/resenas', methods=['POST'])
@token_required
def create_resena(payload):
    data, status = ResenaController.crear(request.get_json(), payload)
    return json_response(data, status)


@app.route('/resenas/<int:id>', methods=['DELETE'])
@token_required
def delete_resena(payload, id):
    data, status = ResenaController.eliminar(id, payload)
    return json_response(data, status)


# ══════════════════════════════════════════════════
# CALIFICACIONES
# ══════════════════════════════════════════════════

@app.route('/calificaciones', methods=['GET'])
def get_calificaciones():
    data, status = CalificacionController.listar(request.args.get('id_juego'))
    return json_response(data, status)


@app.route('/calificaciones/<int:id>', methods=['GET'])
def get_calificacion(id):
    data, status = CalificacionController.obtener(id)
    return json_response(data, status)


@app.route('/calificaciones', methods=['POST'])
@token_required
def create_calificacion(payload):
    data, status = CalificacionController.crear(request.get_json(), payload)
    return json_response(data, status)


@app.route('/calificaciones/<int:id>', methods=['DELETE'])
@token_required
def delete_calificacion(payload, id):
    data, status = CalificacionController.eliminar(id, payload)
    return json_response(data, status)


# ══════════════════════════════════════════════════
# ADMINISTRADORES / PERSONAS
# ══════════════════════════════════════════════════

@app.route('/administradores', methods=['GET'])
@admin_required
def get_administradores(payload):
    data, status = AdminController.listar_administradores()
    return json_response(data, status)


@app.route('/administradores/<int:id>', methods=['GET'])
@admin_required
def get_administrador(payload, id):
    data, status = AdminController.obtener_administrador(id)
    return json_response(data, status)


@app.route('/personas', methods=['GET'])
@admin_required
def get_personas(payload):
    data, status = AdminController.listar_personas()
    return json_response(data, status)


@app.route('/personas/<int:id>', methods=['GET'])
@token_required
def get_persona(payload, id):
    data, status = AdminController.obtener_persona(id, payload)
    return json_response(data, status)


# ══════════════════════════════════════════════════
# LOGS  (MongoDB)
# ══════════════════════════════════════════════════

@app.route('/logs', methods=['GET'])
@admin_required
def get_logs(payload):
    data, status = LogController.listar(
        id_usuario=request.args.get('id_usuario'),
        accion=request.args.get('accion'),
        limit=int(request.args.get('limit', 50)),
    )
    return json_response(data, status)


@app.route('/logs', methods=['POST'])
@token_required
def create_log(payload):
    data, status = LogController.crear_manual(request.get_json(), payload)
    return json_response(data, status)


# ══════════════════════════════════════════════════
# Punto de entrada
# ══════════════════════════════════════════════════

if __name__ == '__main__':
    app.run(debug=True, port=5000)
