 

# 🖥️ PortWatch — Real-Time Port & Process Monitor

> A sleek, cross-platform desktop app to monitor, filter, and kill processes using dev ports — with conflict alerts and customizable port lists via UI.

Built with **Python + Textual TUI** — works on **Windows, macOS, Linux**.

---

## ✨ Features

✅ **Live Process Table** — See all running processes, ports, PIDs, and statuses  
✅ **Dev Port Conflict Detection** — Highlights ports you’ve marked as “dev” (e.g., 3000, 8080)  
✅ **Desktop Notifications** — Get alerts when dev ports are in use ⚠️  
✅ **One-Click Kill** — Terminate any process with confirmation  
✅ **Smart Filters** — Filter by “All”, “New”, or “Conflict”  
✅ **Built-in Port Config UI** — No manual `.portconfig` editing! Add/remove/reset ports via GUI  
✅ **Persistent Config** — Your dev port list is saved automatically to `.portconfig`  
✅ **Cross-Platform** — Works on Windows, macOS, Linux

---

## 🚀 Quick Start

### 1. Install

```bash
pip install portwatch
```

Or if installing from source:

```bash
git clone https://github.com/MadushankaRajapaksha/portwatch
cd portwatch
pip install -e .
```

> Requires Python 3.9+

---

### 2. Run

```bash
portwatch
```

→ Opens interactive TUI app.

---

## 🎯 How to Use

### 🔍 Main Screen

You’ll see a live table of processes using network ports:

| PID  | PORT | PROCESS      | STATUS | ACTION | NOTE         |
|------|------|--------------|--------|--------|--------------|
| 1234 | 3000 | node.exe     | LISTEN | KILL   | 🆕 NEW       |
| 5678 | 5432 | postgres.exe | LISTEN | KILL   | ⚠️ Conflict  |

---

### ⚙️ Manage Dev Ports (NO MANUAL FILE EDITING!)

Click the **“⚙️ Config”** button → opens **Port Config Modal**

- ➕ **Add Port** — Type port number (e.g., `3001`) → click “Add Port”
- 🗑️ **Delete Port** — Select row → click “Delete Selected”
- 🔄 **Reset to Default** — Restores common dev ports (3000, 8080, 5432, etc.)
- ❌ **Close** — Saves automatically — no manual `.portconfig` editing needed!

> ✅ All changes are saved instantly to `.portconfig` — you never need to touch the file.

---

### 🧭 Filter Processes

Use the filter bar:

- **Text Filter** — Type app name or port (e.g., “node” or “3000”)
- **Toggle Filters**:
  - `All` — Show everything
  - `🆕 New` — Only processes appeared since last scan
  - `⚠️ Conflict` — Only processes using your marked dev ports

---

### ☠️ Kill a Process

1. Click any row in the table (or use arrow keys + Enter)
2. Confirm “Kill?” in popup
3. Process is terminated — table auto-refreshes

---

### 🔔 Notifications

When a process starts using a **dev port** (e.g., 3000), you’ll get a desktop notification:

> “⚠️ Port 3000 in use by node.exe”

> ❗ If notifications don’t work, you’ll see a one-time alert modal explaining it.

---

## 📁 Configuration

Your dev port list is stored in `.portconfig` in the app directory — **but you should never edit it manually**.

Example auto-generated `.portconfig`:

```yaml
'3000': React Dev
'8080': Backend API
'5432': PostgreSQL
'27017': MongoDB
```

> ✍️ Use the “⚙️ Config” UI to manage this — it’s safer and instantly reloads in the app.

---

## 🛠️ Troubleshooting

### ❌ “Notifications not working”

- Windows: Make sure “Focus Assist” is off
- macOS: Go to System Settings → Notifications → Allow notifications for Terminal/Python
- Linux: Install `libnotify-bin` → `sudo apt install libnotify-bin`

App will show a warning modal if notifications are disabled.

---

### 🐛 App crashes or shows errors

Run in dev mode for logs:

```bash
textual run -d portwatch
```

---

## 📦 Dependencies

- `textual` — TUI framework
- `psutil` — Process/port scanning
- `plyer` — Desktop notifications
- `pyyaml` — Config file handling

---

## 📄 License

MIT — Use freely for personal or commercial projects.

---

## 🙌 Contributing

PRs welcome! Especially for:

- Export/import config
- Process graphs
- Dark/light mode toggle
- Keyboard shortcuts

---

## 💬 Support

Open an issue on GitHub or message @yourusername.

---

> 🔐 **No more manual `.portconfig` editing** — Use the UI. It’s faster, safer, and updates live.

---

✅ Save this as `README.md` in your project root.

---

## 🧩 Bonus: Add to `setup.py` or `pyproject.toml`

If distributing via pip:

```toml
[project]
name = "portwatch"
version = "0.1.0"
description = "Real-time port and process monitor with dev port alerts"
readme = "README.md"
```

 