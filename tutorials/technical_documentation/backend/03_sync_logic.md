# Part 3: Sync Logic - Background Worker & Diffing

This tutorial explains how data synchronization works between the local cache and Google Sheets.

## Background Sync Worker

A daemon thread runs continuously:

```python
def _sync_worker(self):
    while True:
        # 1. If local DB is empty, pull initial data
        if self._is_empty():
            self.pull_from_remote()
        
        # 2. Push any pending local changes
        self.sync_now()
        
        # 3. Sleep based on user settings
        time.sleep(self.settings.get("sync_frequency", 300))
```

---

## Sync Operations

### `sync_now()` - Push Changes
Processes the `pending_sync` queue one item at a time:
1. Connect to Google Sheets
2. For each pending change (create/update/delete), apply to remote
3. Remove from queue only if successful

### `pull_from_remote()` - Download All Data
Fetches all records from each worksheet and replaces local cache:
```python
for res in ['Vendors', 'Wallets', 'Expenses', 'Payments', 'Deposits']:
    data[res] = worksheet.get_all_records()
```

### `full_sync()` - Push + Pull
The unified sync operation:
```python
def full_sync(self):
    self.sync_now()        # Push local changes first
    self.pull_from_remote()  # Then get latest cloud state
```

---

## Diffing System

The `get_diff()` method compares local and cloud data:

```python
def get_diff(self):
    remote_data = self._fetch_remote_data()
    
    diff = {
        "pending_push": len(self.pending_sync),
        "pending_pull": 0,
        "details": {...}
    }
    
    # Count items in remote not in local
    for rid in remote_ids:
        if rid not in local_ids:
            diff["pending_pull"] += 1
```

### Smart Comparison
Handles type mismatches (string "200" vs number 200):
```python
try:
    if float(remote_value) != float(local_value):
        is_different = True
except:
    if str(remote_value) != str(local_value):
        is_different = True
```

---

## API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/sync/status` | GET | Current sync state |
| `/sync/diff` | GET | Detailed comparison |
| `/sync/force` | POST | Trigger full sync |
| `/sync/pull` | POST | Force overwrite local |
| `/sync/settings` | POST | Update frequency |
