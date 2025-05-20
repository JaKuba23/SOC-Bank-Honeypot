from flask import request, jsonify
from functools import wraps
import os

API_TOKEN = os.environ.get("API_TOKEN", "token")

def require_api_token(func):
    @wraps(func)
    def check_token(*args, **kwargs):
        token = request.headers.get('X-API-KEY')
        if token != API_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return check_token