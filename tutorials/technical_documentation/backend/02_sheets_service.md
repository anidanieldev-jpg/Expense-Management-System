# Part 2: SheetsService - Core Business Logic

The `SheetsService` class in `services/sheets.py` is the heart of the backend.

## Initialization

```python
class SheetsService:
    def __init__(self):
        self.local_data = {}       # In-memory cache
        self.pending_sync = []     # Queue of changes to push
        self.settings = {"sync_frequency": 300}
        
        self._load_local_db()      # Load from local_db.json
        self._load_sync_log()      # Load pending changes
        self._load_settings()      # Load user preferences
        
        # Start background sync thread
        self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()
```

## Offline-First Architecture

All CRUD operations work on the **local cache first**, then queue changes for sync:

```python
def create(self, resource, data):
    with self.lock:
        self.local_data[resource].append(data)
        self._save_local_db_unlocked()
        self._log_change('create', resource, data)  # Queue for sync
    return data
```

This means:
- App works instantly, even offline
- Changes are persisted locally in `local_db.json`
- Changes are logged to `pending_sync.json` for later upload

---

## CRUD Methods

| Method | Description |
| :--- | :--- |
| `get_all(resource)` | Returns all records from local cache |
| `get_by_id(resource, id)` | Finds single record by ID |
| `create(resource, data)` | Adds to cache + logs change |
| `update(resource, id, updates)` | Modifies record + logs change |
| `delete(resource, id)` | Removes record + logs change |

---

## Google Sheets Connection

```python
def _connect(self):
    creds = Credentials.from_service_account_file(self.creds_file, scopes=self.scopes)
    client = gspread.authorize(creds)
    sheet_id = os.getenv('SPREADSHEET_ID')
    return client.open_by_key(sheet_id)
```

Uses:
- Service account credentials from `credentials.json`
- Spreadsheet ID from `.env` file
- Returns a `gspread` Spreadsheet object
