# Google Sheets Backend Setup Guide

This guide details how to configure Google Sheets to act as the database for the Expense Manager App.

## Phase 1: Google Cloud Platform (GCP) Setup

1.  **Create a Project**:
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Click the project dropdown at the top and select **"New Project"**.
    *   Name it (e.g., "Expense-Manager-DB") and create it.

2.  **Enable APIs**:
    *   In the sidebar, go to **"APIs & Services" > "Library"**.
    *   Search for **"Google Sheets API"** and click **Enable**.
    *   Go back to the Library, search for **"Google Drive API"**, and click **Enable**.

3.  **Create Service Account**:
    *   Go to **"APIs & Services" > "Credentials"**.
    *   Click **"Create Credentials"** > **"Service Account"**.
    *   Name it (e.g., "expense-backend").
    *   Click **"Create and Continue"**.
    *   (Optional) Grant "Editor" role (Project > Editor) to ensure it can read/write.
    *   Click **"Done"**.

4.  **Generate Keys**:
    *   Click on the newly created Service Account email in the list.
    *   Go to the **"Keys"** tab.
    *   Click **"Add Key"** > **"Create new key"**.
    *   Select **JSON** and click **Create**.
    *   A file will download. **Rename this file to `credentials.json`**.
    *   **Move `credentials.json`** to your `app_3/backend/` directory.

## Phase 2: Spreadsheet Configuration

1.  **Create the Sheet**:
    *   Go to [Google Sheets](https://docs.google.com/spreadsheets) and create a generic "Blank" spreadsheet.
    *   Name it (e.g., "Expense Manager Data").

2.  **Share the Sheet**:
    A common mistake is forgetting to give your script permission to see the file.

    *   Open `credentials.json` in a text editor and find the `"client_email"` field.
    *   Copy the email address (e.g., `expense-backend@...iam.gserviceaccount.com`).
    *   Open your Google Sheet (e.g., your Warehouse Product with Price file).
    *   Click **"Share"** and paste that email address, giving it **"Editor"** access.
    *   Uncheck "Notify people" (optional) and click **"Share"**.

3.  **Structure the Data**:
    You must create **4 Tabs (Sheets)** with the exact names and headers below (headers are in Row 1).

    **Tab 1: `Vendors`**
    | Row 1 | A | B | C | D |
    | :--- | :--- | :--- | :--- | :--- |
    | **Header** | id | name | address | phone |

    **Tab 2: `Wallets`**
    | Row 1 | A | B | C | D |
    | :--- | :--- | :--- | :--- | :--- |
    | **Header** | id | name | balance | currency |

    **Tab 3: `Expenses`**
    | Row 1 | A | B | C | D | E | F | G | H |
    | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
    | **Header** | id | vendorId | date | total | balance | status | category | description |

    **Tab 4: `Payments`**
    | Row 1 | A | B | C | D | E | F |
    | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
    | **Header** | id | date | amount | walletId | vendorId | refs |

## Phase 3: Connect Backend

1.  **Get Spreadsheet ID**:
    *   Look at your Spreadsheet URL: `https://docs.google.com/spreadsheets/d/1XyZ...AbC/edit`
    *   The long string between `/d/` and `/edit` is your ID.

2.  **Configure Environment**:
    *   In `app_3/backend/`, create a file named `.env`.
    *   Add the line:
        ```
        SPREADSHEET_ID=your_copied_id_here
        ```

3.  **Run Application**:
    *   Running `python app.py` should now successfully connect!
