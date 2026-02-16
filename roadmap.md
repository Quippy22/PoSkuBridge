# PoSkuBridge Development Roadmap
**Version:** 2.2

---

## Phase 1: Infrastructure & Setup (The Foundation)
**Goal:** Establish the environment and verify file structures.
- [x] **Init Sequence:** Verify folder structure.
- [x] **Backup Engine:** Timestamped backups of the `.db` file on launch.
- [x] **DB Schema V2:** Finalize SQLite structure (`products` for core inventory, `mappings` for vendor aliases).
- [x] **Faker Module:** Update mock data generator to query the new SQLite DB instead of using random logic.

---

## Phase 2: The Parsing Engine (PDF Extraction)
**Goal:** Transform messy supplier PDFs into a clean, human-readable DataFrame.
- [x] **Library Integration:** `pdfplumber` extraction logic.
- [x] **Header Mapping:** Dynamic column recognition (identifying QTY, SKU, DESC columns).
- [x] **Structural Cleanup:** Deduplication of ghost columns and merging of split text.
- [x] **Standardization Hook:** Ensure output is a standard list of objects ready for the UI (keeping original Descriptions intact).

---

## Phase 3: The UI Skeleton (The "Visual" Bridge)
**Goal:** Build the GUI container to visualize the data flow.
- [x] **Main Window:** Setup `ttkbootstrap` Window with valid theme.
- [x] **Tab 1 (Dashboard):** A "Process Log" text area + Buttons.
- [x] **Settings:** A new window for changing the settings.
- [x] **Tab 2 (Triage):** Empty TableView placeholder + "Commit" button (Disabled).
- [x] **Wiring:** Connect to the backend (Threaded App Engine).

---

## Phase 4: Database Interface & Logic (The "Memory")
**Goal:** Implement the "Wide Table" logic and Separation of Concerns in Python.
- [x] **Database Class:** Create the thread-safe way to handle connections.
- [x] **Dynamic Columns:** Ensure new suppliers are added to the (Wide-Table pattern).
- [x] **Product vs. Mapping:**
    - Implement `add_product` (Creates clean master data + keywords).
    - Implement `add_mapping` (Links messy supplier SKU to master data).
- [x] **Keyword Utility:** Implement consistent sanitation.

---

## Phase 5: Logging Infrastructure (The "Black Box")
**Goal:** Implement robust, thread-safe system logging with "Silent" capability and crash protection.
- [x] **Loguru Core & File Sink:** Configure the primary `logger.add()` for file storage with rotation (e.g., 10 MB) and retention.
- [x] **Secondary/Silent logs** Establish the pattern using `logger.bind(visual=False)`.
- [x] **Thread-Safe UI Sink:** Create a custom sink function (or class) that pushes logs to the GUI Dashboard.
    * *Constraint:* Must include a **Filter** to ignore logs bound with `visual=False`.
    * *Mechanism:* Use a `queue.Queue` inside the sink to pass messages from background threads to the Tkinter main loop safely.
- [x] **Crash Immunity:** Wrap critical entry points with the `@logger.catch` decorator to capture full stack traces of unhandled exceptions.
---

## Phase 6: The Matcher Logic (The "Brain")
**Goal:** Connect the Parsed Data to the Database to generate status flags.
- [x] **Query Logic:**
    - **Step 1 (Hard Match):** SQL query for exact Vendor SKU matches in `mappings` table (checking specific Supplier Column).
    - **Step 2 (Soft Match):** Fuzzy keyword scoring against `products` table if no exact match found.
- [x] **Status Assignment:** Tag every row object with:
    - 🟢 **GREEN:** Direct DB hit (Found in Supplier Column).
    - 🟡 **YELLOW:** High confidence prediction (Fuzzy Match).
    - 🔴 **RED:** Unknown/New item.

---

## Phase 7: Interaction & Learning (The Triage)
**Goal:** The Clerk corrects data in the UI and the system learns.
- [x] **Triage Table Implementation:** Render the rows in Tab 2.
    - **Red/Yellow:** Editable Autocomplete Combobox connected to `products` table.
    - **Green:** Read-only view.
- [x] **Catalog Search:** "Magnifying Glass" popup to fuzzy search the `products` table (replacing the need to open Excel).
- [x] **Commit Logic:**
    - **Write-Back:** Insert new confirmed mappings into the `mappings` table via `save_mapping`.
    - **Export:** Generate the final WMS-ready `.xlsx` or `.csv`.
