# PoSkuBridge 🌉

**PoSkuBridge** is a modern desktop automation tool designed to bridge the gap between messy supplier PDF Purchase Orders and structured Warehouse Management Systems (WMS). 

It features a dedicated GUI built with `ttkbootstrap` that allows workers to visualize, correct, and map incoming data before final export.

---

## 🚀 Key Features

* **Desktop GUI:** A clean, modern interface for managing the entire workflow.
* **Intelligent Matching:** 
    * **Hard Match:** Instant recognition of known Vendor SKUs.
    * **Soft Match:** Fuzzy keyword scoring to suggest probable products for unknown items.
* **SQLite Backbone:** A robust local database replaces fragile Excel dependencies for product and mapping storage.
* **Interactive Triage:** 
    * 🟢 **Green:** Auto-matched items (Review only).
    * 🟡 **Yellow:** High-confidence suggestions (Confirm or Edit).
    * 🔴 **Red:** Unknown items (Search and Assign).
* **Self-Learning:** Confirmed mappings are saved back to the database, making the system smarter with every use.

---

## 📂 Project Structure

```text
PoSkuBridge/
├── src/                   # Source Code
│   ├── core/              # Backend Logic (Settings, Parser, Matcher)
│   ├── gui/               # Frontend Logic (Windows, Widgets, Themes)
│   ├── tools/             # Utilities (Database Seeder, Debug scripts)
│   └── main.py            # Application Entry Point
│
├── Data/                  # User-facing folders (The Work Area)
│   ├── Archive/           # Successfully processed source PDFs (History)
│   ├── Input/             # Drop new PDF Purchase Orders here
│   ├── Output/            # Generated Excel/CSV files for WMS import
│   └── Review/            # Failed/Skipped files requiring manual fix
│
└── Internal/              # System files (Hidden/Static Data)
    ├── Backups/           # Automated snapshots of mappings.db
    ├── Logs/              # Error logs and session history
    ├── config.json        # Persistent settings (Theme, Paths, Switches)
    └── mappings.db        # SQLite Database (SKU Links & Vendor Rules)
```

## 🛠️ Tech Stack

- **Language:** Python 3.13+
- **GUI Framework:** `ttkbootstrap` (Modern Tkinter wrapper)
- **Database:** SQLite
- **PDF Parsing:** `pdfplumber`
- **Dependency Management:** `uv`
