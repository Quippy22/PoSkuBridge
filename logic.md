# Logic Specification: PoSkuBridge

---

## 1. System Infrastructure
PoSkuBridge is designed as a modular, human-in-the-loop data pipeline.

* **Master Catalog (`Master_Catalog.xlsx`):** The primary source of truth.
    * **Sheet 1 (Core):** `Warehouse_Code` | `Official_Description` | `Keywords`.
    * **Sheet 2 (Mappings):** `Warehouse_Code` | `Description_Aliases` | `Supplier_Columns...`.
* **System Memory (`system_memory.db`):** A SQLite mirror of Sheet 2 for high-speed lookup and fuzzy matching.
* **Active Log (`Active_Log.xlsx`):** A transient workspace in the `/processing` folder where the Clerk resolves non-automated matches.

---

## 2. The Scoring & Triage Engine
The system audits PO descriptions against the Master Catalog using a **Weighted Density Score**.

### Scoring Rules:
* **Maximum Points:** 10 points × the number of words in the PO description.
* **Full Keyword Match:** +10 points (Exact word found in Master Keywords).
* **Partial Keyword Match:** +5 points (Fuzzy match, e.g., "Reg" vs "Regulator").

### The Traffic Light Logic:
* 🟢 **GREEN (100%):** Exact `Supplier_SKU` match found in the database. (Bypasses human review).
* 🟡 **YELLOW (≥ 70%):** High-confidence match. System suggests the best-scoring code in the Log.
* 🔴 **RED (< 70%):** Low-confidence match. Suggestion is left blank, forcing manual entry.

---

## 3. The Human-in-the-Loop Workflow

1.  **Ingestion:** A PDF PO is dropped into the `/input` folder.
2.  **Sync Check:** The system verifies if `Master_Catalog.xlsx` has been modified since the last database update and re-syncs if necessary.
3.  **Matching:** * Green items are held in an internal buffer.
    * Yellow/Red items are written to `Active_Log.xlsx`.
4.  **Feedback Loop (The Watcher):**
    * The Clerk opens the Log and types **'Y'** (to accept a Yellow) or enters a **[Warehouse Code]** (to resolve a Red).
    * Every time the Clerk saves the file, the system checks for unresolved rows.
    * If rows remain, the Log is regenerated with only the outstanding items.
5.  **Finalization:**
    * New SKU/Alias mappings are written back to **Sheet 2** of the Master Catalog.
    * The production `Delivery.csv` is exported to `/output`.
    * A session history is recorded in the `/history` folder.

---

## 4. History & Audit Trail
Every action is documented in a structured `.txt` format for error tracing and accountability:

`[TIMESTAMP] | [PO_ID] | [FLAG] | [INPUT_TEXT] | [RESULT_CODE] | [METHOD]`
