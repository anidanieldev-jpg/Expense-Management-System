"""
Expense Manager Controller - Modern CustomTkinter UI
A production-ready desktop control panel with frameless window design.
"""

import customtkinter as ctk
import subprocess
import sys
import os
import threading
import queue
import signal
import time
import urllib.request
import urllib.error
import webbrowser
from PIL import Image, ImageDraw
import pystray

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

BACKEND_PORT = 3000
FRONTEND_PORT = 8000
APP_TITLE = "Expense Manager"

# Color Palette
COLORS = {
    "bg": "#f5f6fa",           # App background
    "card": "#ffffff",          # Card background
    "header": "#1f2933",        # Title bar
    "primary": "#22c55e",       # Success / Start
    "danger": "#ef4444",        # Danger / Stop
    "text": "#111827",          # Primary text
    "muted": "#6b7280",         # Secondary text
    "sidebar": "#ffffff",       # Sidebar background
    "logs_bg": "#1e2530",       # Log terminal background
    "logs_text": "#e5e7eb",     # Log text
    "info": "#22c55e",          # INFO log level
    "error": "#ef4444",         # ERROR log level
    "warning": "#f59e0b",       # WARNING log level
}

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION CLASS
# ══════════════════════════════════════════════════════════════════════════════

class ExpenseManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Configuration
        self.title(APP_TITLE)
        self.geometry("900x600")
        self.minsize(800, 500)
        self.configure(fg_color=COLORS["bg"])
        
        # Frameless window
        self.overrideredirect(True)
        
        # State
        self.backend_process = None
        self.frontend_process = None
        self.is_running = False
        self.log_queue = queue.Queue()
        
        # Dragging state
        self._drag_start_x = 0
        self._drag_start_y = 0
        
        # Build UI
        self._create_title_bar()
        self._create_main_layout()
        
        # System Tray
        self.tray_icon = None
        self._setup_tray()
        
        # Log processor
        self.after(100, self._process_log_queue)
        
        # Center window on screen
        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    # ══════════════════════════════════════════════════════════════════════════
    # TITLE BAR
    # ══════════════════════════════════════════════════════════════════════════

    def _create_title_bar(self):
        """Custom frameless title bar with drag support"""
        self.title_bar = ctk.CTkFrame(
            self, 
            height=60, 
            fg_color=COLORS["header"], 
            corner_radius=0
        )
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)
        
        # Bind drag events
        self.title_bar.bind("<Button-1>", self._start_drag)
        self.title_bar.bind("<B1-Motion>", self._on_drag)
        
        # Left: App Title
        title_label = ctk.CTkLabel(
            self.title_bar,
            text=APP_TITLE,
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(side="left", padx=20)
        title_label.bind("<Button-1>", self._start_drag)
        title_label.bind("<B1-Motion>", self._on_drag)
        
        # Right: Window Controls Frame
        controls_frame = ctk.CTkFrame(self.title_bar, fg_color="transparent")
        controls_frame.pack(side="right", padx=10)
        
        # Close Button
        self.btn_close = ctk.CTkButton(
            controls_frame,
            text="✕",
            width=40,
            height=35,
            fg_color="transparent",
            hover_color=COLORS["danger"],
            text_color="#ffffff",
            font=ctk.CTkFont(size=16),
            command=self._quit_app
        )
        self.btn_close.pack(side="right", padx=2)
        
        # Minimize Button
        self.btn_minimize = ctk.CTkButton(
            controls_frame,
            text="─",
            width=40,
            height=35,
            fg_color="transparent",
            hover_color="#4a5568",
            text_color="#ffffff",
            font=ctk.CTkFont(size=16),
            command=self._minimize_to_tray
        )
        self.btn_minimize.pack(side="right", padx=2)
        
        # Status Badge
        self.status_frame = ctk.CTkFrame(controls_frame, fg_color="#2d3748", corner_radius=15)
        self.status_frame.pack(side="right", padx=15)
        
        self.status_dot = ctk.CTkLabel(
            self.status_frame,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["danger"]
        )
        self.status_dot.pack(side="left", padx=(10, 5))
        
        self.status_text = ctk.CTkLabel(
            self.status_frame,
            text="SYSTEM STOPPED",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#ffffff"
        )
        self.status_text.pack(side="left", padx=(0, 10), pady=8)

    def _start_drag(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_drag(self, event):
        x = self.winfo_x() + (event.x - self._drag_start_x)
        y = self.winfo_y() + (event.y - self._drag_start_y)
        self.geometry(f"+{x}+{y}")

    # ══════════════════════════════════════════════════════════════════════════
    # MAIN LAYOUT
    # ══════════════════════════════════════════════════════════════════════════

    def _create_main_layout(self):
        """Create sidebar + main content area"""
        # Container for sidebar and content
        self.main_container = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        
        # Configure grid
        self.main_container.grid_columnconfigure(0, weight=0)  # Sidebar fixed
        self.main_container.grid_columnconfigure(1, weight=1)  # Content expands
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self._create_sidebar()
        
        # Main Content
        self._create_content_area()

    def _create_sidebar(self):
        """Left sidebar with controls"""
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            width=200,
            fg_color=COLORS["sidebar"],
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(15, 0), pady=15)
        self.sidebar.grid_propagate(False)
        
        # Controls Header
        controls_label = ctk.CTkLabel(
            self.sidebar,
            text="Controls",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text"]
        )
        controls_label.pack(anchor="w", padx=20, pady=(20, 15))
        
        # Start Button
        self.btn_start = ctk.CTkButton(
            self.sidebar,
            text="▶  Start System",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color="#16a34a",
            text_color="#ffffff",
            height=45,
            corner_radius=8,
            command=self._start_system
        )
        self.btn_start.pack(fill="x", padx=15, pady=(0, 10))
        
        # Stop Button
        self.btn_stop = ctk.CTkButton(
            self.sidebar,
            text="⏹  Stop System",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=COLORS["danger"],
            hover_color="#dc2626",
            text_color="#ffffff",
            height=45,
            corner_radius=8,
            state="disabled",
            command=self._stop_system
        )
        self.btn_stop.pack(fill="x", padx=15, pady=(0, 10))

    def _create_content_area(self):
        """Main content with status cards and logs"""
        self.content = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS["bg"],
            corner_radius=0
        )
        self.content.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        
        # Configure grid for content
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(0, weight=0)  # Cards
        self.content.grid_rowconfigure(1, weight=1)  # Logs
        
        # Status Cards
        self._create_backend_card()
        self._create_frontend_card()
        
        # Logs Panel
        self._create_logs_panel()

    def _create_backend_card(self):
        """Backend API status card"""
        self.backend_card = ctk.CTkFrame(
            self.content,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color="#e5e7eb"
        )
        self.backend_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 15))
        
        # Card Title
        ctk.CTkLabel(
            self.backend_card,
            text="Backend API",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Status Row
        status_row = ctk.CTkFrame(self.backend_card, fg_color="transparent")
        status_row.pack(anchor="w", padx=20)
        
        self.backend_dot = ctk.CTkLabel(
            status_row,
            text="●",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["danger"]
        )
        self.backend_dot.pack(side="left")
        
        self.backend_status = ctk.CTkLabel(
            status_row,
            text="Stopped",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["muted"]
        )
        self.backend_status.pack(side="left", padx=(5, 0))
        
        # Port Info
        ctk.CTkLabel(
            self.backend_card,
            text=f"Port: {BACKEND_PORT}",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["muted"]
        ).pack(anchor="w", padx=20, pady=(10, 20))

    def _create_frontend_card(self):
        """Frontend App status card"""
        self.frontend_card = ctk.CTkFrame(
            self.content,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color="#e5e7eb"
        )
        self.frontend_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 15))
        
        # Card Title
        ctk.CTkLabel(
            self.frontend_card,
            text="Frontend App",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Status Row
        status_row = ctk.CTkFrame(self.frontend_card, fg_color="transparent")
        status_row.pack(anchor="w", padx=20)
        
        self.frontend_dot = ctk.CTkLabel(
            status_row,
            text="●",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["danger"]
        )
        self.frontend_dot.pack(side="left")
        
        self.frontend_status = ctk.CTkLabel(
            status_row,
            text="Stopped",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["muted"]
        )
        self.frontend_status.pack(side="left", padx=(5, 0))
        
        # Port + Open Button Row
        port_row = ctk.CTkFrame(self.frontend_card, fg_color="transparent")
        port_row.pack(fill="x", padx=20, pady=(10, 20))
        
        ctk.CTkLabel(
            port_row,
            text=f"Port: {FRONTEND_PORT}",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["muted"]
        ).pack(side="left")
        
        self.btn_open_app = ctk.CTkButton(
            port_row,
            text="Open App",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#e5e7eb",
            hover_color="#d1d5db",
            text_color=COLORS["text"],
            width=80,
            height=28,
            corner_radius=6,
            state="disabled",
            command=self._open_browser
        )
        self.btn_open_app.pack(side="right")

    def _create_logs_panel(self):
        """Terminal-style logs panel"""
        logs_container = ctk.CTkFrame(
            self.content,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color="#e5e7eb"
        )
        logs_container.grid(row=1, column=0, columnspan=2, sticky="nsew")
        
        # Header
        ctk.CTkLabel(
            logs_container,
            text="Live Logs",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Log Textbox
        self.logs_textbox = ctk.CTkTextbox(
            logs_container,
            fg_color=COLORS["logs_bg"],
            text_color=COLORS["logs_text"],
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8,
            border_width=0,
            wrap="word",
            state="disabled"
        )
        self.logs_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Configure log level tags
        self.logs_textbox.tag_config("info", foreground=COLORS["info"])
        self.logs_textbox.tag_config("error", foreground=COLORS["error"])
        self.logs_textbox.tag_config("warning", foreground=COLORS["warning"])

    # ══════════════════════════════════════════════════════════════════════════
    # LOGGING
    # ══════════════════════════════════════════════════════════════════════════

    def log(self, message, level="info"):
        """Thread-safe logging"""
        self.log_queue.put((message, level))

    def _process_log_queue(self):
        """Process queued log messages"""
        while not self.log_queue.empty():
            message, level = self.log_queue.get()
            self.logs_textbox.configure(state="normal")
            self.logs_textbox.insert("end", message + "\n", level)
            self.logs_textbox.see("end")
            self.logs_textbox.configure(state="disabled")
        self.after(100, self._process_log_queue)

    # ══════════════════════════════════════════════════════════════════════════
    # SYSTEM TRAY
    # ══════════════════════════════════════════════════════════════════════════

    def _setup_tray(self):
        """Setup system tray icon"""
        image = Image.new('RGB', (64, 64), color=COLORS["header"])
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill=COLORS["primary"])
        
        menu = pystray.Menu(
            pystray.MenuItem("Open", self._restore_from_tray),
            pystray.MenuItem("Stop System", self._stop_system),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self._quit_app)
        )
        
        self.tray_icon = pystray.Icon("ExpenseManager", image, APP_TITLE, menu)

    def _minimize_to_tray(self):
        """Minimize window to system tray"""
        self.withdraw()
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _restore_from_tray(self, icon=None, item=None):
        """Restore window from tray"""
        self.tray_icon.stop()
        self.after(0, self.deiconify)

    def _quit_app(self, icon=None, item=None):
        """Clean exit"""
        self._stop_system()
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()

    # ══════════════════════════════════════════════════════════════════════════
    # PROCESS MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════════

    def _find_python(self):
        """Find Python executable"""
        base = os.getcwd()
        venv_paths = [
            os.path.join(base, ".venv", "Scripts", "python.exe"),
            os.path.join(base, "venv", "Scripts", "python.exe"),
            os.path.join(base, ".venv", "bin", "python"),
            os.path.join(base, "venv", "bin", "python"),
        ]
        for path in venv_paths:
            if os.path.exists(path):
                return path
        return sys.executable

    def _update_ui_state(self, running):
        """Update all UI elements based on system state"""
        self.is_running = running
        
        if running:
            # Status badge
            self.status_dot.configure(text_color=COLORS["primary"])
            self.status_text.configure(text="SYSTEM RUNNING")
            
            # Buttons
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
            self.btn_open_app.configure(state="normal")
            
            # Cards
            self.backend_dot.configure(text_color=COLORS["primary"])
            self.backend_status.configure(text="Running", text_color=COLORS["primary"])
            self.frontend_dot.configure(text_color=COLORS["primary"])
            self.frontend_status.configure(text="Running", text_color=COLORS["primary"])
        else:
            # Status badge
            self.status_dot.configure(text_color=COLORS["danger"])
            self.status_text.configure(text="SYSTEM STOPPED")
            
            # Buttons
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self.btn_open_app.configure(state="disabled")
            
            # Cards
            self.backend_dot.configure(text_color=COLORS["danger"])
            self.backend_status.configure(text="Stopped", text_color=COLORS["muted"])
            self.frontend_dot.configure(text_color=COLORS["danger"])
            self.frontend_status.configure(text="Stopped", text_color=COLORS["muted"])

    def _start_system(self):
        """Start both servers"""
        if self.is_running:
            return
        
        self.log("[SYSTEM] Starting system...", "info")
        threading.Thread(target=self._start_sequence, daemon=True).start()

    def _start_sequence(self):
        """Start servers in sequence"""
        # Start Backend
        try:
            backend_dir = os.path.join(os.getcwd(), "backend")
            python_exe = self._find_python()
            
            self.backend_process = subprocess.Popen(
                [python_exe, "app.py"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            self.log(f"[BACKEND] Started on port {BACKEND_PORT}", "info")
            threading.Thread(target=self._stream_output, args=(self.backend_process, "BACKEND"), daemon=True).start()
        except Exception as e:
            self.log(f"[BACKEND] Error: {e}", "error")
            return
        
        time.sleep(2)
        
        # Start Frontend
        try:
            frontend_dir = os.path.join(os.getcwd(), "frontend")
            
            self.frontend_process = subprocess.Popen(
                [sys.executable, "-m", "http.server", str(FRONTEND_PORT)],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            self.log(f"[FRONTEND] Started on port {FRONTEND_PORT}", "info")
            threading.Thread(target=self._stream_output, args=(self.frontend_process, "FRONTEND"), daemon=True).start()
        except Exception as e:
            self.log(f"[FRONTEND] Error: {e}", "error")
            return
        
        # Health Check
        time.sleep(1)
        self._health_check(f"http://localhost:{BACKEND_PORT}/", "Backend")
        self._health_check(f"http://localhost:{FRONTEND_PORT}/", "Frontend")
        
        # Update UI
        self.after(0, lambda: self._update_ui_state(True))

    def _stream_output(self, process, name):
        """Stream subprocess output to logs"""
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.log(f"[{name}] {line.strip()}", "info")
                else:
                    break
        except Exception as e:
            self.log(f"[{name}] Stream error: {e}", "error")

    def _health_check(self, url, name):
        """Verify server is responding"""
        for _ in range(5):
            try:
                with urllib.request.urlopen(url, timeout=2) as r:
                    if r.status == 200:
                        self.log(f"[HEALTH] ✓ {name} is responding", "info")
                        return True
            except:
                pass
            time.sleep(1)
        self.log(f"[HEALTH] ✗ {name} not responding", "error")
        return False

    def _stop_system(self, icon=None, item=None):
        """Stop both servers"""
        if not self.is_running:
            return
        
        self.log("[SYSTEM] Stopping system...", "warning")
        
        for proc, name in [(self.backend_process, "BACKEND"), (self.frontend_process, "FRONTEND")]:
            if proc:
                try:
                    if os.name == 'nt':
                        proc.terminate()
                    else:
                        proc.send_signal(signal.SIGINT)
                    proc.wait(timeout=3)
                    self.log(f"[{name}] Stopped", "info")
                except:
                    proc.kill()
                    self.log(f"[{name}] Force killed", "warning")
        
        self.backend_process = None
        self.frontend_process = None
        self.after(0, lambda: self._update_ui_state(False))

    def _open_browser(self):
        """Open app in browser"""
        webbrowser.open(f"http://localhost:{FRONTEND_PORT}")


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    app = ExpenseManagerApp()
    app.mainloop()
