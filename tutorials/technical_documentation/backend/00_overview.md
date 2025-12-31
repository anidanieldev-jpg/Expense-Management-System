# Backend Technical Documentation

This section covers the Python Flask backend that powers the Expense Manager App.

## Architecture Overview

```
backend/
├── app.py              # Flask application entry point
├── db.py               # Singleton service instance
├── utils.py            # Response helper function
├── routes/             # API route blueprints
│   ├── vendors.py
│   ├── wallets.py
│   ├── expenses.py
│   ├── payments.py
│   ├── deposits.py
│   └── sync.py
└── services/
    └── sheets.py       # SheetsService class
```

## Key Components

| Component | Purpose |
| :--- | :--- |
| `app.py` | Flask app setup, CORS, blueprint registration |
| `SheetsService` | All business logic, CRUD, sync operations |
| `routes/*.py` | HTTP endpoints that call the service |

## Documentation

| Part | Description |
| :--- | :--- |
| [01 App Structure](./01_app_structure.md) | Flask setup, CORS, error handling |
| [02 Sheets Service](./02_sheets_service.md) | CRUD operations, local caching |
| [03 Sync Logic](./03_sync_logic.md) | Background worker, diffing, full sync |
