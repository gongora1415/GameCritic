"""
models/database.py
──────────────────
Conexiones y helpers de bajo nivel para SQLite y MongoDB.
Ninguna lógica de negocio aquí, solo acceso a datos.
"""

import sqlite3
from pymongo import MongoClient, DESCENDING

# ── SQLite ────────────────────────────────────────────────────
DATABASE = 'database.db'


def get_db():
    """Devuelve una conexión SQLite con row_factory activado."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ── MongoDB ───────────────────────────────────────────────────
_mongo_client = MongoClient(
    "mongodb+srv://admin:admin@cluster0.jw471dd.mongodb.net/?appName=Cluster0"
)
_mongo_db = _mongo_client['gamecritic']

logs_col     = _mongo_db['logs_actividad']
metadata_col = _mongo_db['metadata_juegos']
tokens_col   = _mongo_db['tokens_jwt']

# Índices TTL y unicidad
tokens_col.create_index("expira_en", expireAfterSeconds=0)
tokens_col.create_index("jti", unique=True)
