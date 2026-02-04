# Logic Specification: PoSkuBridge (v2.0)

---

## 1. System Architecture
PoSkuBridge moves away from Excel-dependency to a robust Desktop App + SQLite architecture.

* **Database (`poskubridge.db`):** The single source of truth.
    * **Table `products`:** The internal master catalog (SKU, Description).
    * **Table `mappings`:** Vendor-specific knowledge (Vendor_SKU -> Internal_SKU).
* **GUI (`ttkbootstrap`):** The interface for all user interactions (Load, Review, Export).

---

## 2. The Matching Engine
The system processes every line item from a PDF through a two-step logic:

### Step 1: The Hard Match (Vendor Knowledge)
* **Input:** `Vendor SKU` from the PDF.
* **Query:** Check the `mappings` table for an exact match.
* **Result:** 
    * If Found -> **🟢 GREEN Flag** (Auto-assign Internal SKU).
    * If Not Found -> Proceed to Step 2.

### Step 2: The Soft Match (Fuzzy Logic)
* **Input:** `Description` from the PDF.
* **Process:** Normalize text (remove special chars, lowercase) and score against keywords in the `products` table.
* **Result:**
    * **High Score (>Threshold):** **🟡 YELLOW Flag** (Suggest best match).
    * **Low Score:** **🔴 RED Flag** (Unknown item).

---

## 3. The User Workflow (The "Triage")

1.  **Ingestion (Tab 1):** 
    * User clicks "Load PDF".
    * System parses the file and runs the Matching Engine.
    * User is automatically switched to Tab 2.

2.  **Review (Tab 2):** 
    * The user is presented with a table of all line items.
    * **Green Rows:** Read-only (Verified).
    * **Yellow Rows:** Dropdown pre-filled with suggestion. User can Confirm or Change.
    * **Red Rows:** Empty dropdown. User must search/select the correct product.

3.  **Completion:**
    * **Commit:** User clicks "Commit" button.
    * **Learning:** New mappings (Red/Yellow resolutions) are saved to the `mappings` table.
    * **Export:** A clean `.xlsx` or `.csv` is generated in the `/export` folder.

---

## 4. Safety & Logging
* **Backups:** The `.db` file is backed up to `/backups` with a timestamp.
* **Audit Logs:** Every session generates a `.txt` log in `/logs` recording:
    * Files processed.
    * User decisions (mappings created).
    * Errors or anomalies.
