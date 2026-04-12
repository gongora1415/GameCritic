GameCritic 
Plataforma de críticas y calificaciones de videojuegos
Para ejecutar el archivo primero vamos a crear el entorno virtual de Python con: python -m venv .venv
Después ejecutamos el entorno virtual con: .\.venv\Scripts\activate
Ejecutamos la base de datos que creará el archivo database.db con el comando: python init_db.py
Ahora instalamos las dependencias necesarias: pip install -r requirements.txt
Para ejecutar el programa ejecutamos lo siguiente: python app.py
En la línea de comandos nos dará un link al cual accederemos con ctrl+click
Luego en la barra del navegador al final agregamos /usuarios para ver los usuarios, y también podremos ver:
/videojuegos, /reseñas, /calificaciones, /administradores, /personas, /logs
<img width="1135" height="619" alt="image" src="https://github.com/user-attachments/assets/69868f64-e42e-40e2-99c0-5335b0286449" />
Se implementó un sistema de persistencia políglota utilizando SQLite para los datos estructurados y MongoDB Atlas para datos dinámicos y logs de actividad, lo que permite almacenar historial de acciones y metadata variable sin afectar el rendimiento de la base de datos principal.

Base de Datos Relacional (SQLite)
Se encarga de almacenar la información estructurada del sistema:

Usuarios
Videojuegos
Reseñas
Calificaciones
Administradores y Personas

Base de Datos NoSQL (MongoDB Atlas)
Se utiliza para almacenar eventos de actividad y metadata dinámica:

Logs de actividad por usuario (login, reseñas, calificaciones)
Metadata variable de videojuegos (plataformas, DLCs, requisitos, idiomas)


Endpoints combinados SQL + MongoDB
Por ejemplo el endpoint http://127.0.0.1:5000/usuarios/1/perfil
<img width="422" height="420" alt="image" src="https://github.com/user-attachments/assets/e48d384d-cf2a-4806-80da-caa52277c765" />
devuelve los datos del usuario desde SQLite junto a sus últimas 10 actividades registradas en MongoDB:

http://127.0.0.1:5000/videojuegos/2/detalle
<img width="545" height="383" alt="image" src="https://github.com/user-attachments/assets/d8e7bd7b-8d59-416a-89b9-b0b86f213799" />

http://127.0.0.1:5000/logs
<img width="306" height="255" alt="image" src="https://github.com/user-attachments/assets/fc3ca783-3b6e-498f-ae9c-50518980f3f3" />

http://127.0.0.1:5000/videojuegos/2/metadata
<img width="379" height="356" alt="image" src="https://github.com/user-attachments/assets/7f6110c1-45da-41ad-aee9-8d0b1cb68404" />
