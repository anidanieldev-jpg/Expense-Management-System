# Part 1: Flask App Structure

This tutorial covers how the Flask backend is organized.

## app.py Overview

```python
from flask import Flask, jsonify
from flask_cors import CORS
from routes import vendors, wallets, expenses, payments, deposits, sync

app = Flask(__name__)
CORS(app, resources={r"/v1/*": {"origins": ["http://localhost:8000", "http://localhost:8080"]}})
```

### Key Concepts

1. **CORS Configuration**: Allows the frontend (running on port 8000/8080) to make requests to the backend (port 3000).

2. **Blueprint Registration**: Each resource has its own route file that's registered as a Flask Blueprint:
```python
app.register_blueprint(vendors.bp)
app.register_blueprint(sync.bp)
# etc.
```

3. **URL Prefix**: All routes use `/v1` prefix for versioning (e.g., `/v1/vendors`).

---

## db.py - The Service Singleton

```python
from services.sheets import SheetsService
service = SheetsService()
```

This creates a single shared instance of `SheetsService` that all routes import. This ensures:
- One connection to Google Sheets
- Shared local cache across all requests
- Single background sync worker

---

## utils.py - Response Helper

```python
def response(code, message, data=None):
    payload = {"code": code, "message": message}
    if data:
        payload.update(data)
    status = 200 if code == 0 else 400
    return jsonify(payload), status
```

Standardizes all API responses with a consistent structure.

---

## Error Handling

Global handlers for 404 and 500 errors return JSON instead of HTML:

```python
@app.errorhandler(404)
def not_found(e):
    return jsonify({"code": 404, "message": "Endpoint not found"}), 404
```

This prevents the frontend from receiving HTML when something goes wrong.
