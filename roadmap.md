# PoSkuBridge Development Roadmap
**Version:** 2.1

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
- [ ] **Tab 2 (Triage):** Empty TableView placeholder + "Commit" button (Disabled).
- [x] **Wiring:** Connect to the backend (Threaded App Engine).

---

## Phase 4: Database Interface & Logic (The "Memory")
**Goal:** Implement the "Wide Table" logic and Separation of Concerns in Python.
- [x] **Database Class:** Create the thread-safe way to handle connections.
- [x] **Dynamic Columns:** Ensure new suppliers are added to the (Wide-Table pattern).
- [x] **Product vs. Mapping:**
    - Implement `add_product` (Creates clean master data + keywords).
    - Implement `add_mapping` (Links messy supplier SKU to master data).
- [ ] **Keyword Utility:** Implement consistent sanitation.

---

## Phase 5: Logging Infrastructure (The "Black Box")
**Goal:** Implement robust system-wide logging for debugging and audit trails.
- [ ] **Core Logger:** Configure standard Python `logging` (FileHandler + StreamHandler).
- [ ] **Thread-Safe Polling:** Ensure logs generated in worker threads are safely passed to the Main Thread.
- [ ] **Visual Logger:** Connect the backend logger to the GUI Dashboard (Tab 1) via a queue.

---

## Phase 6: The Matcher Logic (The "Brain")
**Goal:** Connect the Parsed Data to the Database to generate status flags.
- [ ] **Normalization (Internal):** Create a temporary normalized version of the description *only* for keyword matching (leaving UI data untouched).
- [ ] **Query Logic:**
    - **Step 1 (Hard Match):** SQL query for exact Vendor SKU matches in `mappings` table (checking specific Supplier Column).
    - **Step 2 (Soft Match):** Fuzzy keyword scoring against `products` table if no exact match found.
- [ ] **Status Assignment:** Tag every row object with:
    - 🟢 **GREEN:** Direct DB hit (Found in Supplier Column).
    - 🟡 **YELLOW:** High confidence prediction (Fuzzy Match).
    - 🔴 **RED:** Unknown/New item.

---

## Phase 7: Interaction & Learning (The Triage)
**Goal:** The Clerk corrects data in the UI and the system learns.
- [ ] **Triage Table Implementation:** Render the rows in Tab 2.
    - **Red/Yellow:** Editable Autocomplete Combobox connected to `products` table.
    - **Green:** Read-only view.
- [ ] **Catalog Search:** "Magnifying Glass" popup to fuzzy search the `products` table (replacing the need to open Excel).
- [ ] **Commit Logic:**
    - **Write-Back:** Insert new confirmed mappings into the `mappings` table via `save_mapping`.
    - **Export:** Generate the final WMS-ready `.xlsx` or `.csv`.

---

## Phase 8: Polish & Automation
**Goal:** Final error handling and user experience improvements.
- [ ] **Action Logs:** Save daily session logs to `/logs` for audit trails.
- [ ] **Email Listener (Future):** Optional IMAP integration to auto-download PDFs.
