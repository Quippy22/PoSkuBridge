# PoSkuBridge 🌉

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-ttkbootstrap-4B8BBE?style=for-the-badge&logo=tk&logoColor=white)
![Database](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Manager](https://img.shields.io/badge/Package_Manager-uv-8A2BE2?style=for-the-badge)

**PoSkuBridge** is an enterprise-grade desktop automation tool designed to bridge the operational gap between unstructured Supplier Purchase Orders (PDF) and structured Warehouse Management Systems (WMS).

It replaces fragile manual data entry with a robust, intelligent workflow that visualizes, corrects, and maps incoming inventory data before final export.

---

## 🚀 Key Features

* **Modern Desktop Interface:** A responsive, high-contrast GUI designed for warehouse environments, enabling rapid data verification.
* **Resilient Data Architecture:** Abandoning Excel dependency for a high-performance **SQLite** backbone, ensuring data integrity for thousands of product mappings.
* **Self-Learning System:** Every manual correction is written back to the database, permanently "teaching" the system to recognize that vendor item in the future.
* **Automated Reconciliation Logic:**
    The system employs a multi-stage matching engine to classify incoming data:
    * 🟢 **Validated (Deterministic):** Instant 100% confidence match based on historical `supplier_sku` ↔ `warehouse_code` mappings.
    * 🟡 **Probabilistic (Heuristic):** RapidFuzz token-sort algorithms analyze description keywords to suggest high-probability matches for review.
    * 🔴 **Exception (Manual):** Unrecognized entities are flagged for operator intervention, triggering the integrated search & assignment workflow.

---

## 📂 Project Structure

```text
PoSkuBridge/
├── main.py                    # Application Entry Point
├── src/                       # Source Code
│   ├── core/                  # Backend Logic (Database, Parser, Matcher)
│   ├── gui/                   # Frontend Logic (Windows, Widgets, Themes)
│   ├── lib/                   # Shared Utilities (Sanitizers, Helpers)
│   └── tools/                 # Utilities (Database Seeder, Faker modules)
│
├── Data/                      # Operational Directory (The Work Area)
│   ├── Input/                 # Drop new PDF Purchase Orders here
│   ├── Output/                # Generated CSV/Excel imports for WMS
│   ├── Review/                # Files requiring manual intervention
│   └── Archive/               # History of successfully processed files
│
└── Internal/                  # System & Configuration
    ├── mappings.db            # SQLite Database (Product Master & Mappings)
    ├── config.json            # Persistent user settings
    ├── Logs/                  # Application execution logs
    └── Backups/               # Automated database snapshots
```
---

## 📜 Final Disclaimer

This project was a major milestone in my journey learning Python and Git. It stands as a reminder of where I started—writing code that was questionable at best—and where I ended up.

After countless iterations, multiple "let's delete everything and start over" moments, and one too many `--force` pushes that definitely made my commit history cry, I finally got the hang of general workflow rules. I found a savior in `uv`, which made package management actually enjoyable, and finally figured out how to properly structure a project.

The app is now in a great state, it's fast, functional, and surprisingly stable. But like all good teachers, its job is done. This project is now **officially finished and archived**. It won't be receiving updates, but it served its purpose perfectly as a learning experience. 
