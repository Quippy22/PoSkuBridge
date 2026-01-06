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
│   ├── main.py            # Application Entry Point
│   ├── core/              # Business Logic (Parser, Database, Scoring)
│   ├── gui/               # UI Components (Windows, Tabs, Widgets)
│   └── tools/             # Utility Scripts (Seeders, Maintenance)
├── data/                  # Local Data
│   ├── inbound/           # Drop PDFs here
│   ├── export/            # Final WMS-ready files
│   └── database/          # SQLite Database File
├── backups/               # Automated safety copies of the DB
└── logs/                  # Session audit trails
```

## 🛠️ Tech Stack

- **Language:** Python 3.13+
- **GUI Framework:** `ttkbootstrap` (Modern Tkinter wrapper)
- **Database:** SQLite
- **PDF Parsing:** `pdfplumber`
- **Dependency Management:** `uv`