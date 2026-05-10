"""
views/json_view.py
───────────────────
Vista JSON reutilizable para la API REST.
Serializa datos con soporte para ObjectId de MongoDB y datetime.
"""

import json
from datetime import datetime
from flask import Response
from bson import ObjectId


def json_response(data, status=200) -> Response:
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
