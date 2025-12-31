# Control Panel

The Control Panel provides a modern desktop GUI launcher for the Expense Manager App.

## Quick Start

Double-click `control_panel.bat` in the project root to launch.

---

## launcher_ctk.py (Recommended)

A **modern, production-quality** control panel built with **CustomTkinter**.

### Features
- **Frameless Window** - Custom title bar with drag support
- **System Status Badge** - Visual indicator (● RUNNING / STOPPED)
- **Status Cards** - Backend API and Frontend App status at a glance
- **Live Logs** - Terminal-style log viewer with colored output
- **System Tray** - Minimizes to tray instead of closing
- **Health Checks** - Verifies servers are responding after startup
- **Graceful Shutdown** - Clean process termination

### Screenshot Layout
```
┌──────────────────────────────────────────────────┐
│ Expense Manager                    ● RUNNING  ─ X│
├─────────────┬────────────────────────────────────┤
│  Controls   │  [Backend API]     [Frontend App]  │
│  ▶ Start    │  ● Running         ● Running       │
│  ⏹ Stop     │  Port: 3000        Port: 8000      │
│             ├────────────────────────────────────┤
│             │  Live Logs                         │
│             │  ┌──────────────────────────────┐  │
│             │  │ [INFO] GET /v1/expenses 200  │  │
│             │  │ [INFO] GET /v1/wallets 200   │  │
│             │  └──────────────────────────────┘  │
└─────────────┴────────────────────────────────────┘
```

### Requirements
- Python 3.8+
- `customtkinter`, `pillow`, `pystray` (in `requirements.txt`)

---

## launcher.py (Legacy)

The original Tkinter-based launcher. Still functional but uses the standard OS window frame.

---

## Batch Files

| File | Purpose |
| :--- | :--- |
| `control_panel.bat` | Launches the modern CustomTkinter control panel (silent) |
| `start_app.bat` | Launches the legacy Tkinter control panel |
| `start.bat` | Opens terminal windows for backend + frontend manually |
