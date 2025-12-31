# EMS Backend - Setup Guide

This is the Python Flask backend for the **Expense Management System (EMS)**. It uses Google Sheets as a database with offline-first architecture.

## Prerequisites
- Python 3.8+
- A Google Cloud Project with the **Google Sheets API** and **Google Drive API** enabled
- A **Service Account** with a JSON key file

## Quick Start

```bash
cd backend
pip install flask flask-cors gspread google-auth python-dotenv
python app.py
```
Server runs at: `http://localhost:3000`

---

## Installation

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Google Sheets Configuration:**
   > **Detailed Guide:** [Google Sheets Setup](../tutorials/google_sheets_setup.md)
   
   - Place your service account JSON file as `credentials.json`
   - Create a new Google Sheet and share it with the `client_email` from credentials
   - Create `.env` file:
     ```env
     SPREADSHEET_ID=your_spreadsheet_id_here
     ```

---

## API Endpoints

### Resources
| Endpoint | Methods | Description |
| :--- | :--- | :--- |
| `/v1/vendors` | GET, POST | Manage vendors |
| `/v1/wallets` | GET, POST, PATCH | Manage wallets |
| `/v1/expenses` | GET, POST, PATCH, DELETE | Track expenses |
| `/v1/payments` | GET, POST | Record payments |
| `/v1/deposits` | GET, POST | Record deposits |

### Sync
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/v1/sync/status` | GET | Current sync state |
| `/v1/sync/diff` | GET | Compare local vs cloud |
| `/v1/sync/force` | POST | Full sync (Push + Pull) |
| `/v1/sync/pull` | POST | Force overwrite local |
| `/v1/sync/settings` | POST | Update sync frequency |

---

## Architecture

```
backend/
├── app.py              # Flask app + CORS
├── db.py               # SheetsService singleton
├── utils.py            # Response helper
├── routes/             # API blueprints
└── services/
    └── sheets.py       # All business logic
```

## Documentation
- [API Reference](../api_documentation.md)
- [Technical Docs](../tutorials/technical_documentation/backend/00_overview.md)
