import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import sys
import os
import threading
import queue
import signal
import time
import urllib.request
import urllib.error
from PIL import Image, ImageDraw
import pystray

# Configuration
BACKEND_PORT = 3000
FRONTEND_PORT = 8000  # Fixed: was 8080, should match README
APP_TITLE = "Expense Manager Controller"

class ExpenseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("650x550")
        self.minsize(550, 450)  # Allow resizing with minimum
        
        # State
        self.backend_process = None
        self.frontend_process = None
        self.is_quitting = False
        
        # Queue for thread-safe GUI updates
        self.log_queue = queue.Queue()
        
        # UI Setup
        self.create_widgets()
        
        # System Tray Setup
        self.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)
        self.tray_icon = None
        self.create_tray_icon()
        
        # Log Monitor
        self.after(100, self.process_log_queue)

    def find_python(self):
        """Find Python executable - checks venv first, then system Python"""
        base = os.getcwd()
        
        # Check common venv locations
        venv_paths = [
            os.path.join(base, ".venv", "Scripts", "python.exe"),  # Windows .venv
            os.path.join(base, "venv", "Scripts", "python.exe"),   # Windows venv
            os.path.join(base, ".venv", "bin", "python"),          # Unix .venv
            os.path.join(base, "venv", "bin", "python"),           # Unix venv
        ]
        
        for path in venv_paths:
            if os.path.exists(path):
                self.log(f"[SYSTEM] Using venv Python: {path}", 'system')
                return path
        
        # Fallback to system Python
        self.log("[SYSTEM] No venv found, using system Python", 'system')
        return sys.executable

    def create_tray_icon(self):
        # Create a simple icon image
        image = Image.new('RGB', (64, 64), color=(73, 109, 137))
        d = ImageDraw.Draw(image)
        d.rectangle([16, 16, 48, 48], fill=(255, 255, 255))
        
        menu = pystray.Menu(
            pystray.MenuItem("Show", self.restore_from_tray),
            pystray.MenuItem("Start System", self.start_all_servers),
            pystray.MenuItem("Stop System", self.stop_all_servers),
            pystray.MenuItem("Exit", self.quit_app)
        )
        
        self.tray_icon = pystray.Icon("ExpenseManager", image, "Expense Manager", menu)

    def minimize_to_tray(self):
        self.withdraw()
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_from_tray(self, icon=None, item=None):
        self.tray_icon.stop()
        self.after(0, self.deiconify)

    def quit_app(self, icon=None, item=None):
        self.is_quitting = True
        self.stop_all_servers()
        if self.tray_icon:
            self.tray_icon.stop()
        self.quit()

    def create_widgets(self):
        # --- Header & Main Actions ---
        action_frame = tk.Frame(self, pady=20)
        action_frame.pack(fill=tk.X, padx=20)
        
        lbl_title = tk.Label(action_frame, text="Expense Manager", font=("Segoe UI", 16, "bold"))
        lbl_title.pack(side=tk.TOP, pady=(0, 10))
        
        btn_frame = tk.Frame(action_frame)
        btn_frame.pack()
        
        self.btn_start_all = tk.Button(btn_frame, text="▶ START SYSTEM", command=self.start_all_servers, 
                                       bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"), width=15, height=2)
        self.btn_start_all.pack(side=tk.LEFT, padx=10)
        
        self.btn_stop_all = tk.Button(btn_frame, text="⏹ STOP SYSTEM", command=self.stop_all_servers, 
                                      bg="#F44336", fg="white", font=("Segoe UI", 11, "bold"), width=15, height=2, state=tk.DISABLED)
        self.btn_stop_all.pack(side=tk.LEFT, padx=10)

        # --- Status Section ---
        status_frame = tk.LabelFrame(self, text="System Status", font=("Segoe UI", 10), padx=15, pady=10)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Backend Row
        frame_be = tk.Frame(status_frame)
        frame_be.pack(fill=tk.X, pady=2)
        tk.Label(frame_be, text="Backend API:", width=15, anchor="w", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        self.lbl_backend_status = tk.Label(frame_be, text="⚫ Stopped", fg="gray", font=("Segoe UI", 10))
        self.lbl_backend_status.pack(side=tk.LEFT)
        tk.Label(frame_be, text=f"(Port {BACKEND_PORT})", fg="gray", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=10)

        # Frontend Row
        frame_fe = tk.Frame(status_frame)
        frame_fe.pack(fill=tk.X, pady=2)
        tk.Label(frame_fe, text="Frontend App:", width=15, anchor="w", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        self.lbl_frontend_status = tk.Label(frame_fe, text="⚫ Stopped", fg="gray", font=("Segoe UI", 10))
        self.lbl_frontend_status.pack(side=tk.LEFT)
        tk.Label(frame_fe, text=f"(Port {FRONTEND_PORT})", fg="gray", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=10)
        
        self.btn_open_browser = tk.Button(frame_fe, text="Open App ↗", command=self.open_browser, 
                                          font=("Segoe UI", 9), state=tk.DISABLED, bg="#e3f2fd")
        self.btn_open_browser.pack(side=tk.RIGHT)

        # --- Console ---
        tk.Label(self, text="Live Logs:", anchor="w", font=("Segoe UI", 9)).pack(fill=tk.X, padx=20, pady=(5, 0))
        self.console = scrolledtext.ScrolledText(self, state='disabled', bg="#1e1e1e", fg="#d4d4d4", 
                                                 font=("Consolas", 9), padx=10, pady=10)
        self.console.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Configuring output tags for colors
        self.console.tag_config('backend', foreground='#4ec9b0')   # Cyan
        self.console.tag_config('frontend', foreground='#ce9178') # Orange
        self.console.tag_config('system', foreground='#cccccc')   # Gray
        self.console.tag_config('success', foreground='#6a9955')  # Green
        self.console.tag_config('error', foreground='#f14c4c')    # Red

    def log(self, message, tag='system'):
        self.log_queue.put((message, tag))

    def process_log_queue(self):
        while not self.log_queue.empty():
            msg, tag = self.log_queue.get()
            self.console.config(state='normal')
            self.console.insert(tk.END, msg + "\n", tag)
            self.console.see(tk.END)
            self.console.config(state='disabled')
        self.after(100, self.process_log_queue)

    def set_gui_running(self, is_running):
        if is_running:
            self.btn_start_all.config(state=tk.DISABLED, bg="#a5d6a7")
            self.btn_stop_all.config(state=tk.NORMAL, bg="#F44336")
            self.btn_open_browser.config(state=tk.NORMAL)
        else:
            self.btn_start_all.config(state=tk.NORMAL, bg="#4CAF50")
            self.btn_stop_all.config(state=tk.DISABLED, bg="#ef9a9a")
            self.btn_open_browser.config(state=tk.DISABLED)

    def health_check(self, url, name, retries=5, delay=1):
        """Ping a URL to verify server is actually responding"""
        for i in range(retries):
            try:
                req = urllib.request.Request(url, method='GET')
                with urllib.request.urlopen(req, timeout=2) as response:
                    if response.status == 200:
                        self.log(f"[HEALTH] ✓ {name} is responding", 'success')
                        return True
            except (urllib.error.URLError, urllib.error.HTTPError):
                pass
            time.sleep(delay)
        
        self.log(f"[HEALTH] ✗ {name} not responding after {retries} attempts", 'error')
        return False

    # --- Process Management ---

    def start_all_servers(self, icon=None, item=None):
        if self.backend_process or self.frontend_process:
            return
            
        self.set_gui_running(True)
        threading.Thread(target=self._start_sequence, daemon=True).start()

    def _start_sequence(self):
        self.log(">>> Starting System...", 'system')
        self.start_backend()
        time.sleep(2)  # Give backend time to initialize
        self.start_frontend()
        
        # Health checks
        time.sleep(1)
        self.health_check(f"http://localhost:{BACKEND_PORT}/", "Backend API")
        self.health_check(f"http://localhost:{FRONTEND_PORT}/", "Frontend Server")

    def start_backend(self):
        backend_dir = os.path.join(os.getcwd(), "backend")
        python_exe = self.find_python()
        
        try:
            self.backend_process = subprocess.Popen(
                [python_exe, "app.py"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            self.lbl_backend_status.config(text="🟢 Running", fg="green")
            self.log(f"[BACKEND] Started on Port {BACKEND_PORT}", 'backend')
            
            threading.Thread(target=self.stream_reader, args=(self.backend_process, "[BACKEND]", 'backend'), daemon=True).start()
        except Exception as e:
            self.log(f"[BACKEND] Error: {e}", 'error')
            self.lbl_backend_status.config(text="🔴 Error", fg="red")

    def start_frontend(self):
        frontend_dir = os.path.join(os.getcwd(), "frontend")
        try:
            self.frontend_process = subprocess.Popen(
                [sys.executable, "-m", "http.server", str(FRONTEND_PORT)],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            self.lbl_frontend_status.config(text="🟢 Running", fg="green")
            self.log(f"[FRONTEND] Started on Port {FRONTEND_PORT}", 'frontend')
            
            threading.Thread(target=self.stream_reader, args=(self.frontend_process, "[FRONTEND]", 'frontend'), daemon=True).start()
        except Exception as e:
            self.log(f"[FRONTEND] Error: {e}", 'error')
            self.lbl_frontend_status.config(text="🔴 Error", fg="red")

    def graceful_terminate(self, process, name):
        """Attempt graceful shutdown before force terminate"""
        if process is None:
            return
        
        try:
            # Try SIGINT first (graceful)
            if os.name == 'nt':
                # Windows: send CTRL+C event
                process.send_signal(signal.CTRL_C_EVENT)
            else:
                # Unix: send SIGINT
                process.send_signal(signal.SIGINT)
            
            # Wait up to 3 seconds for graceful shutdown
            try:
                process.wait(timeout=3)
                self.log(f"[{name}] Gracefully stopped", 'system')
                return
            except subprocess.TimeoutExpired:
                pass
        except Exception:
            pass
        
        # Force terminate if graceful failed
        try:
            process.terminate()
            process.wait(timeout=2)
            self.log(f"[{name}] Force terminated", 'system')
        except Exception:
            process.kill()
            self.log(f"[{name}] Force killed", 'error')

    def stop_all_servers(self, icon=None, item=None):
        self.log(">>> Stopping System...", 'system')
        
        if self.backend_process:
            self.graceful_terminate(self.backend_process, "BACKEND")
            self.backend_process = None
            self.lbl_backend_status.config(text="⚫ Stopped", fg="gray")
            
        if self.frontend_process:
            self.graceful_terminate(self.frontend_process, "FRONTEND")
            self.frontend_process = None
            self.lbl_frontend_status.config(text="⚫ Stopped", fg="gray")

        self.set_gui_running(False)

    def open_browser(self):
        import webbrowser
        webbrowser.open(f"http://localhost:{FRONTEND_PORT}")

    def stream_reader(self, process, prefix, tag):
        """Reads output from subprocess and logs it."""
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    clean_line = line.strip()
                    self.log(f"{prefix} {clean_line}", tag)
                else:
                    break
        except Exception as e:
            self.log(f"{prefix} Stream Error: {e}", 'error')
        
        self.log(f"{prefix} Process exited.", tag)

if __name__ == "__main__":
    app = ExpenseApp()
    app.mainloop()
