from flask import jsonify
import random
import datetime

def response(code, message, data=None):
    res = {"code": code, "message": message}
    if data: res.update(data)
    return jsonify(res), 200 if code == 0 else 400

def generate_id(prefix):
    return f"{prefix}-{random.randint(100000, 999999)}"

def today():
    return datetime.date.today().isoformat()
