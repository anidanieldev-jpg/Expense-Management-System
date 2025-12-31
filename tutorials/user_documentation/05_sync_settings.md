# Sync Settings

The **Sync Settings** page allows you to manage the connection between your local app and Google Sheets cloud storage.

## Accessing Sync Settings
Click **"Sync Settings"** in the left sidebar navigation.

---

## Local-First Philosophy
This application follows a **"Local-First, Push-Only"** design.
1.  **Work Offline**: You can add expenses, vendors, and payments without any internet connection. All changes are saved instantly to your device.
2.  **Push to Cloud**: When you are ready, you "Push" your local changes to Google Sheets.
3.  **No Conflicts**: The app never overwrites your local work with cloud data (it does not "Pull").

## Dashboard Overview

### Status
- **Pending Changes (To Push)**: The number of items you have created or edited locally that strictly need to be uploaded.
- **Connection Status**: Indicates if the backend is successfully connected to Google Services.

### Resource Breakdown
A detailed table showing exactly which items are waiting to be pushed:
- **Vendors**: New or edited suppliers.
- **Wallets**: Balance updates or new wallets.
- **Expenses/Payments**: Financial records waiting for upload.

---

## Actions

### Push to Cloud
The main blue button initiates a **Manual Push**:
1. Checks your local transaction log (`diff.json`).
2. Uploads pending items one-by-one to Google Sheets.
3. Removes them from the pending list upon success.

### Auto-Push
The system runs a background worker that automatically attempts to push pending changes every **5 minutes** (default). You don't always need to click the button!

### Hard Reset (Recovery)
⚠️ **Danger Zone**: "Hard Reset Local Data" will delete **ALL** your local data and re-download everything from Google Sheets.
- Use this ONLY if your local data is corrupted or if you want to switch to a fresh state from the cloud.
- **Warning**: Any unsynced local changes will be lost forever.

---

## Troubleshooting

| Symptom | Solution |
| :--- | :--- |
| "Connection Failed" | Check your internet and verify `credentials.json` is valid. |
| Button spins indefinitely | Restart the system via Control Panel (Stop -> Start). |
| Changes not appearing in Sheet | Verify your Service Account has "Editor" access to the Google Sheet. |
