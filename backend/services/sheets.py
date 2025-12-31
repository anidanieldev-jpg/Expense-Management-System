import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv
import json
import threading
import time
import datetime
import traceback

# Load env variables
load_dotenv()

class SheetsService:
    def __init__(self):
        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.creds_file = os.path.join(self.base_path, 'credentials.json')
        self.local_db_file = os.path.join(self.base_path, 'local_db.json')
        self.sync_log_file = os.path.join(self.base_path, 'diff.json')
        self.settings_file = os.path.join(self.base_path, 'settings.json')
        self.local_data = {}
        self.pending_sync = []
        self.settings = {"sync_frequency": 300} # Default 5 mins
        self.last_sync_info = {"time": None, "status": "Never"}
        self.lock = threading.RLock()
        self.sync_lock = threading.Lock()
        
        # Load local data and settings
        self._load_local_db()
        self._load_sync_log()
        self._load_settings()
        
        # Start background sync thread
        self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()

    def _load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            except:
                pass

    def _save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)

    def update_settings(self, new_settings):
        self.settings.update(new_settings)
        self._save_settings()

    def _load_local_db(self):
        if os.path.exists(self.local_db_file):
            try:
                with open(self.local_db_file, 'r') as f:
                    self.local_data = json.load(f)
            except:
                self.local_data = {}
        
        # Ensure structure
        for res in ['Vendors', 'Wallets', 'Expenses', 'Payments', 'Deposits']:
            if res not in self.local_data: self.local_data[res] = []

    def _save_local_db(self):
        with self.lock:
            with open(self.local_db_file, 'w') as f:
                json.dump(self.local_data, f, indent=2)

    def _load_sync_log(self):
        if os.path.exists(self.sync_log_file):
            try:
                with open(self.sync_log_file, 'r') as f:
                    self.pending_sync = json.load(f)
            except:
                self.pending_sync = []
        else:
            self.pending_sync = []

    def _save_sync_log(self):
        with self.lock:
            with open(self.sync_log_file, 'w') as f:
                json.dump(self.pending_sync, f, indent=2)

    def _log_change(self, action, resource, data, id_val=None):
        with self.lock:
            self.pending_sync.append({
                'timestamp': datetime.datetime.now().isoformat(),
                'action': action, # 'create', 'update', 'delete'
                'resource': resource,
                'data': data,
                'id_val': id_val
            })
            self._save_sync_log_unlocked()

    def _save_sync_log_unlocked(self):
        with open(self.sync_log_file, 'w') as f:
            json.dump(self.pending_sync, f, indent=2)

    def _save_sync_log(self):
        with self.lock:
            self._save_sync_log_unlocked()

    def _sync_worker(self):
        """Background thread that pushes local changes to Google Sheets"""
        print("[SYNC] Sync worker started.")
        
        while True:
            # 1. Check if we need to pull initial data
            is_empty = sum(len(v) for v in self.local_data.values() if isinstance(v, list)) == 0
            if is_empty:
                print("[SYNC] Local database is empty. Attempting to pull from remote...")
                success = self.pull_from_remote()
                if not success:
                    print("[SYNC] Initial pull failed. Will retry in 1 minute.")
                    time.sleep(60)
                    continue

            # 2. Daily/Regular Push
            self.sync_now()
            
            # Sync check based on user settings
            freq = self.settings.get("sync_frequency", 300)
            time.sleep(max(10, freq)) # Minimum 10 seconds safety

    def _connect(self):
        """Helper to establish GSheets connection with credentials"""
        try:
            if not os.path.exists(self.creds_file):
                err = f"Credentials file not found at {self.creds_file}"
                print(f"[SYNC] Error: {err}")
                self.last_sync_info["status"] = "Error"
                self.last_sync_info["details"] = err
                return None
            
            creds = Credentials.from_service_account_file(self.creds_file, scopes=self.scopes)
            client = gspread.authorize(creds)
            
            # Use ID from .env for reliability
            sheet_id = os.getenv('SPREADSHEET_ID')
            if not sheet_id:
                err = "SPREADSHEET_ID not found in .env"
                print(f"[SYNC] Error: {err}")
                self.last_sync_info["status"] = "Error"
                self.last_sync_info["details"] = err
                return None

            return client.open_by_key(sheet_id)
        except Exception as e:
            err = str(e)
            print(f"[SYNC] Connection Error: {err}")
            self.last_sync_info["status"] = "Error"
            self.last_sync_info["details"] = err
            return None

    def sync_now(self):
        """Trigger an immediate sync of pending changes"""
        # Prevent concurrent syncs
        if not self.sync_lock.acquire(blocking=False):
            print("[SYNC] Sync already in progress. Skipping.")
            return False

        try:
            if not self.pending_sync:
                return True
                
            print(f"[SYNC] {len(self.pending_sync)} items pending. Attempting sync...")
            try:
                sheet = self._connect()
                if sheet:
                    while True:
                        with self.lock:
                            if not self.pending_sync:
                                break
                            item = self.pending_sync[0]
                        
                        success = self._apply_to_remote(sheet, item)
                        if success:
                            with self.lock:
                                self.pending_sync.pop(0)
                                self._save_sync_log_unlocked()
                        else:
                            break # Stop and retry later if remote fails
                    
                    print(f"[SYNC] Push successful: {len(self.pending_sync)} items synced.")
                    self.last_sync_info = {
                        "time": datetime.datetime.now().isoformat(),
                        "status": "Success",
                        "details": "Changes pushed"
                    }
                    print("[SYNC] Sync cycle completed.")
                    return True
                else:
                    self.last_sync_info["status"] = "Failed"
                    self.last_sync_info["details"] = "Connection failed during push"
                    print("[SYNC] Connection failed during push. Will retry later.")
                    return False
            except Exception as e:
                self.last_sync_info["status"] = "Error"
                self.last_sync_info["details"] = str(e)
                print(f"[SYNC] Error during sync push: {str(e)}")
                return False
        finally:
            self.sync_lock.release()

    def _save_local_db_unlocked(self):
        with open(self.local_db_file, 'w') as f:
            json.dump(self.local_data, f, indent=2)

    def _fetch_remote_data(self, sheet=None):
        """Internal helper to pull all records from GSheets without saving"""
        try:
            if not sheet: sheet = self._connect()
            if not sheet: return None
            
            data = {}
            for res in ['Vendors', 'Wallets', 'Expenses', 'Payments', 'Deposits']:
                try:
                    ws = sheet.worksheet(res)
                    data[res] = ws.get_all_records()
                except:
                    data[res] = []
            return data
        except:
            return None

    def get_diff(self):
        """Calculates differences based on local diff.json only"""
        # Local-First optimization: No remote fetch
        
        diff = {
            "pending_push": 0,
            "pending_pull": 0,
            "details": {
                "Vendors": {"push": 0, "pull": 0},
                "Wallets": {"push": 0, "pull": 0},
                "Expenses": {"push": 0, "pull": 0},
                "Payments": {"push": 0, "pull": 0},
                "Deposits": {"push": 0, "pull": 0}
            }
        }
        
        # Snapshot local state safely
        with self.lock:
            pending_snapshot = list(self.pending_sync)

        diff["pending_push"] = len(pending_snapshot)

        # Calculate Pushes (from pending sync log)
        for item in pending_snapshot:
            res = item['resource']
            if res in diff["details"]:
                diff["details"][res]["push"] += 1
                
        return diff, None

    def full_sync(self):
        """Manual Push operation (Local-First)"""
        print("[SYNC] Manually Triggered: Starting Push Sync...")
        # 1. Push all pending changes
        push_success = self.sync_now()
        
        if push_success:
            print("[SYNC] Manual Push Sync: SUCCESS.")
        else:
            print(f"[SYNC] Manual Push Sync: COMPLETED WITH ISSUES (Push: {'OK' if push_success else 'FAIL'})")
        
        return self.last_sync_info

    def pull_from_remote(self):
        """Fetch all data from Google Sheets to populate local cache"""
        if not self.sync_lock.acquire(blocking=False):
             print("[SYNC] Sync/Pull already in progress. Skipping pull.")
             return False

        try:
            print("[SYNC] Connecting for remote pull...")
            data = self._fetch_remote_data()
            if data:
                with self.lock:
                    self.local_data = data
                    self._save_local_db_unlocked()
                
                self.last_sync_info = {
                    "time": datetime.datetime.now().isoformat(),
                    "status": "Success",
                    "details": "Full pull complete"
                }
                print("[SYNC] Full pull complete.")
                return True
            else:
                self.last_sync_info["status"] = "Failed"
                self.last_sync_info["details"] = "Connection failed for pull"
                return False
        finally:
            self.sync_lock.release()

    def _apply_to_remote(self, sheet, item):
        """Applies a single logged change to the remote Google Sheet"""
        try:
            res = item['resource']
            action = item['action']
            data = item['data']
            id_val = item['id_val']
            
            ws = sheet.worksheet(res)
            
            if action == 'create':
                headers = ws.row_values(1)
                if not headers:
                    headers = list(data.keys())
                    ws.append_row(headers)
                
                # Ensure all lists/dicts are strings for Sheets
                row_data = {}
                for k, v in data.items():
                    if isinstance(v, (list, dict)):
                        row_data[k] = json.dumps(v)
                    else:
                        row_data[k] = v
                
                row = [row_data.get(h, '') for h in headers]
                ws.append_row(row)
                return True
                
            elif action == 'update':
                col_values = ws.col_values(1)
                try:
                    row_idx = col_values.index(str(id_val)) + 1
                    headers = ws.row_values(1)
                    
                    # Ensure all lists/dicts are strings for Sheets
                    row_data = {}
                    for k, v in data.items():
                        if isinstance(v, (list, dict)):
                            row_data[k] = json.dumps(v)
                        else:
                            row_data[k] = v
                            
                    new_row = [row_data.get(h, '') for h in headers]
                    ws.update(f"A{row_idx}", [new_row])
                    return True
                except ValueError:
                    return True 
                    
            elif action == 'delete':
                col_values = ws.col_values(1)
                try:
                    row_idx = col_values.index(str(id_val)) + 1
                    ws.delete_rows(row_idx)
                    return True
                except ValueError:
                    return True
                    
            return False
        except Exception as e:
            print(f"[SYNC] Worker failed on item: {str(e)}")
            return False

    # --- CRUD Operations (NOW ALWAYS LOCAL) ---

    def get_all(self, resource):
        return self.local_data.get(resource, [])

    def get_by_id(self, resource, id_val):
        records = self.get_all(resource)
        for r in records:
            if str(r.get('id')) == str(id_val): return r
        return None

    def create(self, resource, data):
        with self.lock:
            if resource not in self.local_data: self.local_data[resource] = []
            self.local_data[resource].append(data)
            self._save_local_db_unlocked()
            self._log_change('create', resource, data)
        return data

    def update(self, resource, id_val, updates):
        with self.lock:
            records = self.local_data.get(resource, [])
            for i, r in enumerate(records):
                if str(r.get('id')) == str(id_val):
                    records[i] = {**r, **updates}
                    self._save_local_db_unlocked()
                    self._log_change('update', resource, records[i], id_val)
                    return records[i]
        return None

    def _revert_transaction(self, resource, id_val):
        """Reverts the financial impact of a transaction before deletion"""
        # Only relevant for financial transactions
        if resource not in ['Payments', 'Deposits']:
            return

        # We must find the record to know the amount and wallet
        item = self.get_by_id(resource, id_val)
        if not item: return

        wallet_id = item.get('walletId')
        try:
            amount = float(item.get('amount', 0))
        except:
            return # Invalid amount

        if not wallet_id: return

        wallet = self.get_by_id('Wallets', wallet_id)
        if not wallet: return # Wallet deleted? Can't revert.

        try:
            current_balance = float(wallet.get('balance', 0))
            
            new_balance = current_balance
            if resource == 'Payments':
                # Payment decreased balance, so add it back
                new_balance += amount
            elif resource == 'Deposits':
                # Deposit increased balance, so remove it
                new_balance -= amount
                
            # Log the wallet update (Recursively uses RLock)
            self.update('Wallets', wallet_id, {'balance': new_balance})
            print(f"[LOGIC] Reverted {resource} {id_val}: Wallet {wallet_id} balance adjusted to {new_balance}")

            # Revert Expense Balances (if Payment)
            if resource == 'Payments':
                refs = item.get('refs', [])
                if isinstance(refs, str):
                    try: refs = json.loads(refs)
                    except: refs = []
                
                for r in refs:
                    if isinstance(r, dict) and 'id' in r and 'amount' in r:
                        exp_id = r['id']
                        alloc_amt = float(r['amount'])
                        
                        exp = self.get_by_id('Expenses', exp_id)
                        if exp:
                             # Restore balance
                             cur_exp_bal = float(exp.get('balance', 0))
                             restored_bal = cur_exp_bal + alloc_amt
                             
                             # Restore Status (Simplistic logic: if bal > 0, it's Partial or Open)
                             # Since we don't know the Original Amount easily without parsing 'amount' field which is total cost
                             # We'll just set to 'Partial' if not fully unpaid? 
                             # Actually usually 'Open' or 'Pending'. Let's check Expense fields.
                             # Assuming 'amount' is total cost.
                             total_cost = float(exp.get('amount', 0))
                             status = 'Partial'
                             if restored_bal >= total_cost - 0.01: status = 'Pending' # Using Pending/Unpaid convention
                             
                             self.update('Expenses', exp_id, {'balance': restored_bal, 'status': status})
                             print(f"[LOGIC] Reverted Expense {exp_id}: Balance += {alloc_amt}")
        except Exception as e:
            print(f"[ERROR] Failed to revert transaction {id_val}: {e}")

    def _check_dependencies(self, resource, id_val):
        """Checks if the record is referenced by others. Raises Exception if so."""
        id_str = str(id_val)
        
        if resource == 'Wallets':
            for p in self.local_data.get('Payments', []):
                if str(p.get('walletId')) == id_str:
                    raise Exception(f"Cannot delete Wallet. Used in Payment {p['id']}")
            for d in self.local_data.get('Deposits', []):
                if str(d.get('walletId')) == id_str:
                    raise Exception(f"Cannot delete Wallet. Used in Deposit {d['id']}")

        elif resource == 'Vendors':
            for e in self.local_data.get('Expenses', []):
                if str(e.get('vendorId')) == id_str:
                    raise Exception(f"Cannot delete Vendor. Has link to Expense {e['id']}")
            for p in self.local_data.get('Payments', []):
                if str(p.get('vendorId')) == id_str:
                    raise Exception(f"Cannot delete Vendor. Has link to Payment {p['id']}")
            for d in self.local_data.get('Deposits', []):
                if str(d.get('vendorId')) == id_str:
                    raise Exception(f"Cannot delete Vendor. Has link to Deposit {d['id']}")

        elif resource == 'Expenses':
            for p in self.local_data.get('Payments', []):
                refs = p.get('refs', [])
                # Handle potential string format from legacy/remote data
                if isinstance(refs, str):
                    try: refs = json.loads(refs)
                    except: refs = []
                    
                # Legacy ref was list of IDs; New ref is list of {id, amount}
                ref_ids = []
                for r in refs:
                    if isinstance(r, dict): ref_ids.append(str(r.get('id')))
                    else: ref_ids.append(str(r))

                if id_str in ref_ids:
                     raise Exception(f"Cannot delete Expense. It is part of Payment {p['id']}")

    def delete(self, resource, id_val):
        with self.lock:
            # 1. Validation: Check for dependencies
            # 1. Validation: Check for dependencies
            self._check_dependencies(resource, id_val)

            # 2. Revert financial impact
            self._revert_transaction(resource, id_val)

            # 3. Proceed with deletion
            records = self.local_data.get(resource, [])
            initial_len = len(records)
            self.local_data[resource] = [r for r in records if str(r.get('id')) != str(id_val)]
            if len(self.local_data[resource]) < initial_len:
                self._save_local_db_unlocked()
                self._log_change('delete', resource, None, id_val)
                return True
        return False

    def process_payment(self, payment_data):
        wallet_id = payment_data['walletId']
        amount = float(payment_data['amount'])
        allocations = payment_data['allocations']
        
        wallet = self.get_by_id('Wallets', wallet_id)
        if not wallet: raise Exception("Wallet not found")
        
        current_balance = float(wallet['balance'])
        if current_balance < amount:
            raise Exception(f"Insufficient funds. Balance: {current_balance}")

        # Atomic operations on local cache
        self.update('Wallets', wallet_id, {'balance': current_balance - amount})

        self.create('Payments', {
            'id': payment_data['id'],
            'date': payment_data['date'],
            'amount': amount,
            'walletId': wallet_id,
            'vendorId': payment_data['vendorId'],
            'vendorId': payment_data['vendorId'],
            'refs': allocations # Store full allocation objects for reversal
        })

        for alloc in allocations:
            exp_id = alloc['id']
            alloc_amt = float(alloc['amount'])
            expense = self.get_by_id('Expenses', exp_id)
            if expense:
                new_bal = max(0, float(expense['balance']) - alloc_amt)
                self.update('Expenses', exp_id, {
                    'balance': new_bal,
                    'status': 'Paid' if new_bal == 0 else 'Partial'
                })
        return True

    def process_deposit(self, deposit_data):
        wallet_id = deposit_data['walletId']
        amount = float(deposit_data['amount'])
        
        wallet = self.get_by_id('Wallets', wallet_id)
        if not wallet: raise Exception("Wallet not found")
        
        current_balance = float(wallet['balance']) if wallet.get('balance') else 0

        self.update('Wallets', wallet_id, {'balance': current_balance + amount})

        self.create('Deposits', {
            'id': deposit_data['id'],
            'date': deposit_data['date'],
            'amount': amount,
            'walletId': wallet_id,
            'vendorId': deposit_data.get('vendorId', ''), 
            'source': 'Vendor Transfer',
            'notes': deposit_data.get('notes', '')
        })
        return True
