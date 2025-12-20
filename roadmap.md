# PoSkuBridge Development Roadmap
**Version:** 1.0 | **Project Lead:** Developer | **Status:** Initiated

---

## Phase 1: The "Walking Skeleton" (Infrastructure)
**Goal:** Establish the environment, automated initialization, and safety backups.
- [ ] **Init Sequence:** Script to verify/create folder structure (`/input`, `/processing`, `/output`, `/history`).
- [ ] **Database Setup:** Initialize SQLite `system_memory.db` with tables for `Core_Inventory` and `Mappings`.
- [ ] **Master Catalog Generation:** Create `Master_Catalog.xlsx` template if not present.
- [ ] **Backup Engine:** Implement a timestamped backup routine for the `.db` and `.xlsx` files on every system launch.
- [ ] **Faker Module:** Create a script to generate "Mock POs" (JSON/CSV) to test logic without real PDFs.

---

## Phase 2: The Parsing Engine (PDF Ingestion)
**Goal:** Transform messy supplier PDFs into structured data.
- [ ] **Library Integration:** Set up `pdfplumber` or `pypdf` for table extraction.
- [ ] **Header Mapping:** Logic to identify "SKU", "Description", "Price", and "Qty" regardless of column order.
- [ ] **Text Normalization:** Strip special characters and lowercase all input for matching consistency.

---

## Phase 3: The Scoring & Triage Engine (The Brain)
**Goal:** Implement the 70% weighted density logic for automated decision-making.
- [ ] **Scoring Algorithm:** Compare PO words against Master Keywords (+10 for full, +5 for partial).
- [ ] **Triage Logic:** - 🟢 **Green:** Direct SKU hit (Move to buffer).
    - 🟡 **Yellow:** 70%+ score (Suggest best guess).
    - 🔴 **Red:** <70% score (Manual entry required).
- [ ] **Evaluation Trigger:** Generate `Catalog_Evaluation.xlsx` and trigger "Auto-Open" for the Clerk.

---

## Phase 4: The Loop & History (Human-in-the-Loop)
**Goal:** Monitor clerk work, validate inputs, and record actions.
- [ ] **The Watcher:** Implement `watchdog` to monitor `Catalog_Evaluation.xlsx` for save events.
- [ ] **Live Validation:** Check for unresolved Red items upon save; prevent finalization if incomplete.
- [ ] **Catalog Sync:** Automated write-back of new SKU/Alias mappings to `Master_Catalog.xlsx`.
- [ ] **Action Log:** Generate structured `.txt` in `/history` for every session.

---

## Phase 5: Export & The "Smell Test"
**Goal:** Final output production and high-level error detection.
- [ ] **CSV Production:** Generate the final WMS-ready delivery file.
- [ ] **The "Smell Test" Flag:** Implement custom logic to flag statistical outliers (e.g., unusual quantities or historical mapping mismatches).
- [ ] **Persistent CLI:** Finalize the main loop with clean console outputs and "Awaiting new PO..." status.

---

## Phase 6: Full Automation (The Ingestor)
**Goal:** Eliminate manual handling of input files.
- [ ] **Email Listener:** Add an IMAP thread to auto-download PDF attachments from a specific inbox.
- [ ] **Excel Management:** Implement the auto-close logic for `Catalog_Evaluation.xlsx` once processing is verified.
- [ ] **Final CLI Polish:** High-visibility status updates for the Clerk’s dashboard.
