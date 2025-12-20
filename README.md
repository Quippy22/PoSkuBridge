# PoSkuBridge 🌉

**PoSkuBridge** is a lightweight, human-in-the-loop automation tool designed to bridge the gap between messy supplier PDF Purchase Orders and structured Warehouse Management Systems (WMS). 

It uses a weighted keyword scoring engine to suggest matches, allowing a worker to verify data via Excel before final CSV exportation.

---

## 🚀 Key Features

* **Weighted Scoring Engine:** Uses a 70% confidence threshold to triage items into Green (Auto), Yellow (Suggest), or Red (Manual) flags.
* **Excel as UI:** Leverages familiar spreadsheets (`Catalog_Evaluation.xlsx`) for human intervention.
* **Persistent CLI:** A dedicated console window provides real-time status updates on ingestion and processing.
* **Automated Sync:** Keeps a local SQLite database in sync with a master Excel catalog.
* **Safety First:** Automated backups of databases and master files on every launch.

---

## 📂 Project Structure

```text
PoSkuBridge/
├── src/                   # Source Code (The Engine)
│   ├── main.py            # CLI Entry point & Status Loop
│   ├── core/              # Business Logic (Scoring, Watcher, DB Sync)
│   ├── utils/             # Technical Utilities (Parsers, Excel Ctrl, Backups)
├── data/                  # Site-Specific Data (Git-ignored content)
│   ├── Master_Catalog.xlsx # Human-editable Source of Truth
│   ├── inbound/           # Drop PDFs here
│   ├── active/            # Catalog_Evaluation.xlsx workspace
│   └── export/            # Final WMS-ready CSVs
├── database/              # SQLite Persistent Storage
├── backup/                # Automated safety copies (DB & Master)
└── logs/                  # Session audit trails (.txt)
