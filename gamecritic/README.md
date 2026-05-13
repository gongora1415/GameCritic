# GameCritic
**Plataforma de críticas y calificaciones de videojuegos**

Para ejecutar el archivo primero vamos a crear el entorno virtual de Python con:
```bash
python -m venv .venv
```

Después ejecutamos el entorno virtual con:
```bash
.\.venv\Scripts\activate
```

Ejecutamos la base de datos que creará el archivo `database.db` con el comando:
```bash
python init_db.py
```

Ahora instalamos las dependencias necesarias:
```bash
pip install -r requirements.txt
```

Para ejecutar el programa ejecutamos lo siguiente:
```bash
python app.py
```

En la línea de comandos nos dará un link al cual accederemos con `ctrl+click`

Luego en la barra del navegador al final agregamos `/usuarios` para ver los usuarios, y también podremos ver:
`/videojuegos` `/resenas` `/calificaciones` `/administradores` `/personas` `/logs`

![image](https://github.com/user-attachments/assets/69868f64-e42e-40e2-99c0-5335b0286449)

---

## Base de datos

Se implementó un sistema de persistencia políglota utilizando SQLite para los datos estructurados y MongoDB Atlas para datos dinámicos y logs de actividad, lo que permite almacenar historial de acciones y metadata variable sin afectar el rendimiento de la base de datos principal.

### Base de Datos Relacional (SQLite)

Se encarga de almacenar la información estructurada del sistema:
- Usuarios
- Videojuegos
- Reseñas
- Calificaciones
- Administradores y Personas

### Base de Datos NoSQL (MongoDB Atlas)

Se utiliza para almacenar eventos de actividad y metadata dinámica:
- Logs de actividad por usuario (login, reseñas, calificaciones)
- Metadata variable de videojuegos (plataformas, DLCs, requisitos, idiomas)

### Endpoints combinados SQL + MongoDB

Por ejemplo el endpoint `http://127.0.0.1:5000/usuarios/1/perfil`

![image](https://github.com/user-attachments/assets/e48d384d-cf2a-4806-80da-caa52277c765)

devuelve los datos del usuario desde SQLite junto a sus últimas 10 actividades registradas en MongoDB.

`http://127.0.0.1:5000/videojuegos/2/detalle`

![image](https://github.com/user-attachments/assets/d8e7bd7b-8d59-416a-89b9-b0b86f213799)

`http://127.0.0.1:5000/logs`

![image](https://github.com/user-attachments/assets/fc3ca783-3b6e-498f-ae9c-50518980f3f3)

`http://127.0.0.1:5000/videojuegos/2/metadata`

![image](https://github.com/user-attachments/assets/7f6110c1-45da-41ad-aee9-8d0b1cb68404)

---

## Credenciales de prueba

| Email | Contraseña | Rol |
|---|---|---|
| admin@games.com | admin123 | Admin |
| juan@games.com | juan456 | User |

---

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

---

## Tecnologías

- **Backend:** Flask · SQLite (datos relacionales) · MongoDB Atlas (logs + metadata + JWT)
- **Auth:** JWT (PyJWT) con revocación por JTI en MongoDB · bcrypt para contraseñas
- **Frontend:** SPA vanilla JS · CSS custom properties · Bebas Neue + DM Sans

---

## Estructura del proyecto

```
gamecritic/
│
├── app.py                        ← Punto de entrada, rutas Flask
├── init_db.py                    ← Setup SQLite + helpers bcrypt
├── requirements.txt
├── database.db                   ← Generado por init_db.py
│
├── models/                       ← Acceso a datos
│   ├── database.py               ← Conexiones SQLite y MongoDB
│   ├── usuario.py
│   ├── videojuego.py
│   ├── resena.py                 ← Reseñas y calificaciones
│   ├── log.py                    ← Logs en MongoDB
│   └── token.py                  ← JWT en MongoDB
│
├── controllers/                  ← Lógica de negocio
│   ├── auth_controller.py        ← Registro, login, logout
│   ├── usuario_controller.py
│   ├── videojuego_controller.py
│   ├── resena_controller.py
│   └── log_controller.py
│
└── views/                        ← Respuestas HTTP y frontend
    ├── json_view.py              ← Serialización JSON
    ├── auth_decorators.py        ← @token_required / @admin_required
    ├── templates/
    │   └── index.html            ← SPA frontend
    └── static/
        ├── css/style.css
        └── js/app.js
```
