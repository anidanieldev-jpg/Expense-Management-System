# Expense Manager App

A full-stack expense management system with **Google Sheets synchronization**, offline-first architecture, and a modern SPA frontend.

## Key Features

*   **Vendor Management**: Track suppliers and their outstanding debts.
*   **Expense Tracking**: Record bills, view balances, and monitor payment status.
*   **Unified Transfers**: Single interface for making **Payments** (Money Out) and receiving **Deposits** (Money In).
*   **Smart Wallets**: Automatic balance updates with visual transaction history.
*   **Google Sheets Sync**: Real-time synchronization with configurable frequency.
    *   **Local-First Architecture**: Changes are saved instantly offline and queued for upload.
    *   **Push-Only Sync**: Manual "Push to Cloud" button to upload pending changes.
    *   **Auto-Push**: Background worker automatically syncs pending changes every 5 minutes.
    *   **Offline Resilient**: Works seamlessly offline; syncs when connection is available.

---

## ⚙️ Initial Setup (Required)

Before running the application, you must configure the connection to Google Sheets.

### 1. Google Cloud Credentials
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project (or select an existing one).
3.  Enable the **Google Sheets API** and **Google Drive API**.
4.  Create a **Service Account** and download the JSON key file.
5.  Rename the file to `credentials.json` and place it in the `backend/` folder.
    *   *Path:* `backend/credentials.json`

### 2. Prepare Google Sheet
1.  Create a new Google Sheet.
2.  Get the `SPREADSHEET_ID` from the URL (e.g., `docs.google.com/spreadsheets/d/YOUR_ID_HERE/edit`).
3.  **Share the Sheet**: Click "Share" and add the **client_email** found in your `credentials.json` file as an **Editor**.

### 3. Environment Configuration
1.  Navigate to the `backend/` folder.
2.  Rename `.env.example` to `.env`.
3.  Open `.env` and paste your Spreadsheet ID:
    ```
    SPREADSHEET_ID=your_actual_spreadsheet_id
    ```

---

## Quick Start

### Option 1: Modern Control Panel (Recommended)
Double-click `control_panel.bat` to launch the modern graphical dashboard. It handles servers, logs, and health checks automatically.

### Option 2: Manual Start

**1. Start the Backend (Python Flask)**
```powershell
cd backend
pip install -r ../requirements.txt  # First time only
python app.py
```
Backend runs at: [http://localhost:3000](http://localhost:3000)

**2. Start the Frontend (Static Server)**
```powershell
cd frontend
python -m http.server 8000
```
Frontend runs at: [http://localhost:8000](http://localhost:8000)

---

## Project Structure

```
expense-manager/
├── backend/                 # Flask API Server
│   ├── app.py              # Main application entry
│   ├── routes/             # API route blueprints
│   ├── services/           # Business logic (SheetsService)
│   ├── credentials.json    # Google Service Account (YOU MUST ADD THIS)
│   └── .env                # Environment Variables (YOU MUST ADD THIS)
├── frontend/               # SPA Web Application
│   ├── index.html          # Main HTML shell
│   ├── js/                 # JavaScript modules
│   └── css/                # Stylesheets
├── control_panel/          # Desktop launcher utilities
├── tutorials/              # Documentation
│   ├── user_documentation/ # End-user guides
│   └── technical_documentation/ # Developer tutorials
└── control_panel.bat       # Modern GUI launcher
```

---

## Documentation

*   📘 **[User Guide](./tutorials/user_documentation/00_overview.md)** - End-user manual for managing vendors, expenses, and wallets.
*   🛠️ **[Technical Documentation](./tutorials/overview.md)** - Complete architecture guide, code walkthroughs (Frontend & Backend), and API reference.
*   📡 **[API Reference](./api_documentation.md)** - Quick access to backend endpoints.

---

## Requirements

*   Python 3.8+
*   Flask, gspread, google-auth, python-dotenv
*   Modern browser (Chrome, Firefox, Edge)
