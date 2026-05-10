# GameCritic — API REST + SPA Frontend (MVC)

## Estructura del proyecto

```
gamecritic/
│
├── app.py                  ← Punto de entrada · rutas Flask (Vista HTTP)
├── init_db.py              ← Setup SQLite + helpers bcrypt
├── requirements.txt
├── database.db             ← SQLite (copiar aquí el archivo original)
│
├── models/                 ── MODELO ──────────────────────────────────
│   ├── __init__.py
│   ├── database.py         ← Conexiones SQLite y MongoDB
│   ├── usuario.py          ← CRUD tabla usuarios + persona
│   ├── videojuego.py       ← CRUD tabla videojuegos + metadata MongoDB
│   ├── resena.py           ← CRUD tablas resenas y calificaciones
│   ├── log.py              ← Colección logs_actividad (MongoDB)
│   └── token.py            ← Colección tokens_jwt (MongoDB) · JWT
│
├── controllers/            ── CONTROLADOR ──────────────────────────────
│   ├── __init__.py
│   ├── auth_controller.py        ← registro / login / logout
│   ├── usuario_controller.py     ← listar / obtener / eliminar / perfil
│   ├── videojuego_controller.py  ← CRUD juegos + metadata
│   ├── resena_controller.py      ← CRUD reseñas y calificaciones
│   └── log_controller.py         ← logs + admin (administradores/personas)
│
└── views/                  ── VISTA ────────────────────────────────────
    ├── json_view.py          ← Serialización JSON (ObjectId, datetime)
    ├── auth_decorators.py    ← @token_required / @admin_required
    ├── templates/
    │   └── index.html        ← SPA frontend completo
    └── static/ (servido por Flask)
        ├── css/style.css     ← Diseño editorial oscuro
        └── js/app.js         ← Lógica SPA (fetch API, vistas dinámicas)
```

## Cómo ejecutar

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Copiar la base de datos original
cp /ruta/a/database.db .

# (Opcional) Reinicializar la BD con datos de prueba
python init_db.py

# 3. Levantar el servidor
python app.py
```

Abrir **http://localhost:5000** en el navegador.

## Credenciales de prueba

| Email              | Contraseña | Rol   |
|--------------------|------------|-------|
| admin@games.com    | admin123   | Admin |
| juan@games.com     | juan456    | User  |

## Flujo MVC

```
Request HTTP
    │
    ▼
app.py (Ruta / Vista)
    │  extrae parámetros del request
    │  aplica decorador auth si aplica
    ▼
Controller
    │  valida reglas de negocio
    │  orquesta modelos
    ▼
Model
    │  ejecuta SQL en SQLite
    │  o consulta/escribe en MongoDB
    ▼
Controller  (devuelve tuple data, status)
    │
    ▼
json_response(data, status)  ← Vista JSON
    │
    ▼
Response HTTP  →  SPA Frontend (index.html + app.js)
```

## Tecnologías

- **Backend**: Flask, SQLite (datos relacionales), MongoDB Atlas (logs + metadata + JWT)
- **Auth**: JWT (PyJWT) con revocación por JTI en MongoDB · bcrypt para contraseñas
- **Frontend**: SPA vanilla JS · CSS custom properties · Bebas Neue + DM Sans
