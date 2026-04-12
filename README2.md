# GameCritic 🎮
**Plataforma de críticas de videojuegos** — Persistencia políglota: SQLite + MongoDB

---

## Arquitectura de Datos

| Capa | Motor | Datos almacenados |
|---|---|---|
| SQL | SQLite | Usuarios, videojuegos, reseñas, calificaciones, administradores |
| NoSQL | MongoDB | Logs de actividad, metadata dinámica de juegos |

---

## Instalación y ejecución

### 1. Clonar y crear entorno virtual
```bash
git clone <url-del-repo>
cd gamecritic
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Instalar y arrancar MongoDB

**Windows** — [Descargar MongoDB Community](https://www.mongodb.com/try/download/community)
```bash
mongod --dbpath C:\data\db
```

**Linux / macOS (Homebrew)**
```bash
brew tap mongodb/brew && brew install mongodb-community
brew services start mongodb-community
```

> Por defecto la app conecta a `mongodb://localhost:27017/`. Para usar MongoDB Atlas
> exporta la variable de entorno:
> ```bash
> export MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/"
> ```

### 4. Inicializar la base de datos SQLite
```bash
python init_db.py
```

### 5. Ejecutar la aplicación
```bash
python app.py
```
Servidor disponible en: `http://127.0.0.1:5000`

---

## Endpoints disponibles

### Usuarios (SQL)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/usuarios` | Listar todos |
| GET | `/usuarios/<id>` | Obtener uno |
| POST | `/usuarios` | Crear usuario |
| DELETE | `/usuarios/<id>` | Eliminar usuario |

### 🔀 Endpoints combinados SQL + NoSQL
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/usuarios/<id>/perfil` | Perfil completo: datos SQL + últimas 10 actividades (MongoDB) |
| GET | `/videojuegos/<id>/detalle` | Juego SQL + metadata dinámica + promedio calificaciones |

### Videojuegos (SQL)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/videojuegos` | Listar todos |
| GET | `/videojuegos/<id>` | Obtener uno |
| POST | `/videojuegos` | Crear juego |
| PUT | `/videojuegos/<id>` | Actualizar juego |
| DELETE | `/videojuegos/<id>` | Eliminar juego |

### Metadata Dinámica de Juegos (MongoDB)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/videojuegos/<id>/metadata` | Obtener metadata |
| POST | `/videojuegos/<id>/metadata` | Crear/reemplazar metadata |
| PUT | `/videojuegos/<id>/metadata` | Actualizar campos específicos |
| DELETE | `/videojuegos/<id>/metadata` | Eliminar metadata |

### Logs de Actividad (MongoDB)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/logs` | Listar logs (filtros: `?id_usuario=1&accion=nueva_reseña&limit=20`) |
| POST | `/logs` | Insertar log manual |

### Reseñas / Calificaciones / Admin (SQL)
Mismos endpoints de la Entrega 1.

---

## Ejemplos de uso

### Crear metadata dinámica para un juego
```bash
curl -X POST http://localhost:5000/videojuegos/1/metadata \
  -H "Content-Type: application/json" \
  -d '{
    "plataformas": ["PC", "PS5", "Xbox Series X"],
    "idiomas": ["Español", "Inglés", "Polaco"],
    "requisitos_minimos": {
      "SO": "Windows 10 64-bit",
      "RAM": "8 GB",
      "GPU": "NVIDIA GTX 1060"
    },
    "dlcs": ["Blood and Wine", "Hearts of Stone"],
    "multijugador": false,
    "precio_usd": 39.99
  }'
```

### Consultar perfil completo (SQL + MongoDB)
```bash
curl http://localhost:5000/usuarios/2/perfil
```

### Filtrar logs de un usuario
```bash
curl "http://localhost:5000/logs?id_usuario=2&limit=10"
```
