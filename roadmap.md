# PoSkuBridge Development Roadmap
**Version:** 2.0 | **Architecture:** Python + SQLite + ttkbootstrap (Desktop App)

---

## Phase 1: Infrastructure & Database (The Foundation)
**Goal:** Establish the SQLite database as the single source of truth and verify environment.
- [x] **Init Sequence:** Verify folder structure (`/inbound`, `/export`, `/logs`).
- [x] **Backup Engine:** Timestamped backups of the `.db` file on launch.
- [ ] **DB Schema V2:** Finalize SQLite structure (`products` for core inventory, `mappings` for vendor aliases).
- [ ] **Faker Module:** Update mock data generator to query the new SQLite DB instead of using random logic.

---

## Phase 2: The Parsing Engine (PDF Extraction)
**Goal:** Transform messy supplier PDFs into a clean, human-readable DataFrame.
- [x] **Library Integration:** `pdfplumber` extraction logic.
- [x] **Header Mapping:** Dynamic column recognition (identifying QTY, SKU, DESC columns).
- [x] **Structural Cleanup:** Deduplication of ghost columns and merging of split text.
- [ ] **Standardization Hook:** Ensure output is a standard list of objects ready for the UI (keeping original Descriptions intact).

---

## Phase 3: The UI Skeleton (The "Visual" Bridge)
**Goal:** Build the GUI container to visualize the data flow.
- [x] **Main Window:** Setup `ttkbootstrap` Window with valid theme.
- [x] **Tab 1 (Dashboard):** A "Process Log" text area + Buttons.
- [ ] **Tab 2 (Triage):** Empty TableView placeholder + "Commit" button (Disabled).
- [ ] **Wiring:** Connect to the backend

---

## Phase 4: The Matcher Logic (The "Brain")
**Goal:** Connect the Parsed Data to the Database to generate status flags.
- [ ] **Normalization (Internal):** Create a temporary normalized version of the description *only* for keyword matching (leaving UI data untouched).
- [ ] **Query Logic:**
    - **Step 1 (Hard Match):** SQL query for exact Vendor SKU matches in `mappings` table.
    - **Step 2 (Soft Match):** Fuzzy keyword scoring against `products` table if no exact match found.
- [ ] **Status Assignment:** Tag every row object with:
    - 🟢 **GREEN:** Direct DB hit.
    - 🟡 **YELLOW:** High confidence prediction.
    - 🔴 **RED:** Unknown/New item.

---

## Phase 5: Interaction & Learning (The Triage)
**Goal:** The Clerk corrects data in the UI and the system learns.
- [ ] **Triage Table Implementation:** Render the rows in Tab 2.
    - **Red/Yellow:** Editable Autocomplete Combobox connected to `products` table.
    - **Green:** Read-only view.
- [ ] **Catalog Search:** "Magnifying Glass" popup to fuzzy search the `products` table (replacing the need to open Excel).
- [ ] **Commit Logic:**
    - **Write-Back:** Insert new confirmed mappings into the `mappings` table.
    - **Export:** Generate the final WMS-ready `.xlsx` or `.csv`.

---

## Phase 6: Polish & Automation
**Goal:** Final error handling and user experience improvements.
- [ ] **Smell Test:** Flag statistical outliers (e.g., unusually high quantities).
- [ ] **Action Logs:** Save daily session logs to `/logs` for audit trails.
- [ ] **Email Listener (Future):** Optional IMAP integration to auto-download PDFs.
