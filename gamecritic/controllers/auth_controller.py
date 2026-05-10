"""
controllers/auth_controller.py
───────────────────────────────
Lógica de negocio para autenticación: registro, login, logout.
Cada método recibe los datos ya extraídos del request y devuelve
un tuple (data, http_status).
"""

import sqlite3
from init_db import hash_password, verificar_password
from models  import UsuarioModel, TokenModel, LogModel


class AuthController:

    @staticmethod
    def registro(nombre: str, email: str, contrasena: str, edad=None):
        if len(contrasena) < 8:
            return {"error": "La contraseña debe tener al menos 8 caracteres"}, 400

        contrasena_hash = hash_password(contrasena)
        try:
            new_id = UsuarioModel.create(nombre, email, contrasena_hash, edad)
        except sqlite3.IntegrityError:
            return {"error": "Ya existe una cuenta con ese correo"}, 409

        LogModel.registrar(new_id, "registro_usuario", {"nombre": nombre, "email": email})
        return {"id_usuario": new_id, "nombre": nombre, "email": email}, 201

    @staticmethod
    def login(email: str, contrasena: str):
        usuario = UsuarioModel.get_by_email(email)
        password_ok = (
            usuario is not None
            and verificar_password(contrasena, usuario['contrasena'])
        )
        if not password_ok:
            return {"error": "Credenciales incorrectas"}, 401

        rol   = "admin" if UsuarioModel.is_admin(usuario['id_usuario']) else "user"
        token = TokenModel.generar(usuario['id_usuario'], usuario['email'], rol)

        LogModel.registrar(usuario['id_usuario'], "login", {"rol": rol})
        return {
            "token":     token,
            "tipo":      "Bearer",
            "expira_en": TokenModel.expira_en(),
            "usuario": {
                "id_usuario": usuario['id_usuario'],
                "nombre":     usuario['nombre'],
                "email":      usuario['email'],
                "rol":        rol,
            },
        }, 200

    @staticmethod
    def logout(payload: dict):
        jti = payload.get("jti")
        TokenModel.revocar(jti)
        LogModel.registrar(int(payload['sub']), "logout", {"jti": jti[:8] + "..."})
        return {"message": "Sesión cerrada correctamente"}, 200
