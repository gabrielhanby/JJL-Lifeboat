🧾 Hanby CRUD System – User Manual

──────────────────────────────────────────────  
🧠 SYSTEM RULES & DESIGN  
──────────────────────────────────────────────  

• Every table must include:  
 - UUID (per-entity unique identifier)  
 - IND (per-UUID index starting at 0)  

• Registry table must exist:  
 - Contains only UUID  
 - Tracks all created UUIDs  

• sqlite_sequence and Registry are the only tables exempt from UUID/IND rules.  

• All database interactions flow through the toolchain in this fixed order:  
 create → update → delete → read  

──────────────────────────────────────────────  
🛠️ STARTUP – connect.py  
──────────────────────────────────────────────  

Path: ../utils/connect.py  

On import:  
• Loads ../settings/database.json to locate the target .db file  
• Validates schema on startup:  
 - All tables (except Registry & sqlite_sequence) must include UUID and IND  
 - Registry must only contain UUID  
• Connects to SQLite using check_same_thread=False  
• Builds shared state:  
 - conn → SQLite connection  
 - cursor → Shared cursor  
 - db_meta → { "tables": [...], "fields": [[...], [...]] }  

This shared state is passed to all tools.  

──────────────────────────────────────────────  
📦 CRUD PACKAGE FORMATS  
──────────────────────────────────────────────  

✅ CREATE  
{
  "create": {
    "group_1": {
      "table": ["Contacts", "Notes"],
      "field": [
        ["first_name", "middle_name", "last_name"],
        ["subject", "body"]
      ],
      "value": [
        ["Gabriel", "Joseph", "Hanby"],
        ["Test Note", "This is an example test note."]
      ]
    }
  }
}  

✅ READ  
{
  "read": {
    "UUID": ["uuid_1", "uuid_2"]
  }
}  

✅ UPDATE  
{
  "update": {
    "uuid_1": {
      "table": ["Notes"],
      "field": [["subject", "body"]],
      "IND": [["new_1", "new_1"]],
      "value": [["Follow-up", "Another note"]]
    }
  }
}  

✅ DELETE  
{
  "delete": {
    "uuid_1": {
      "where": ["Notes", "Notes"],
      "IND": ["1", "2"]
    },
    "uuid_2": {
      "where": ["all"],
      "IND": [""]  // ignored
    }
  }
}  

──────────────────────────────────────────────  
🔁 PACKAGE DISPATCH – query.py  
──────────────────────────────────────────────  

Path: ../utils/query.py  

• submit_request(pkg) buffers incoming packages  
• 3-second timer resets with every new package  
• When the timer expires:  
 - Packages are grouped by tool type:  
  → CREATE: all group_n merged under one package  
  → READ: all UUIDs combined into one list  
  → UPDATE & DELETE: UUID keys merged into single objects  
• Combined packages are dispatched sequentially to tools in this order:  
 1. create.py  
 2. update.py  
 3. delete.py  
 4. read.py  
• Tools run synchronously on shared conn/cursor/db_meta  
• last_results stores each tool’s output for retrieval  

──────────────────────────────────────────────  
📤 HOW TO SUBMIT A PACKAGE  
──────────────────────────────────────────────  

From CLI or test file:  
from utils import query  
query.submit_request(package)  

• The 3-second timer starts on the first request  
• If no new packages arrive in 3s, the batch is dispatched automatically  

──────────────────────────────────────────────  
✅ ALL TOOLS OUTPUT FORMAT  
──────────────────────────────────────────────  

Each tool returns a standardized dict with exactly three keys:  

{
  "status": "success" | "partial" | "error",
  "errors": [ ... ],
  "action": { ... tool-specific data ... }
}  

---

### Tool-specific action keys:

- create.py:  
  "action": {  
    "created": [/* list of new UUIDs */],  
    "inserts": { "Contacts": 3, "Notes": 2 }  
  }  

- update.py:  
  "action": {  
    "updates": { "Contacts": 1 },  
    "inserts": { "Notes": 1 }  
  }  

- delete.py:  
  "action": {  
    "deleted_rows": { "Contacts": 2, "Notes": 1 },  
    "removed_uuids": [/* list of UUIDs removed from Registry */]  
  }  

- read.py:  
  "action": {  
    "results": {  
      "uuid_1": { "Contacts": [...], "Notes": [...] },  
      "uuid_2": { ... }  
    }  
  }  

──────────────────────────────────────────────  
🧩 CREATE TOOL  
──────────────────────────────────────────────  

• Accepts multiple tables per UUID (groups)  
• Auto-increments IND per UUID per table  
• Validates fields exist  
• Adds UUID to Registry  

──────────────────────────────────────────────  
🧩 READ TOOL  
──────────────────────────────────────────────  

• Reads all rows from all tables per UUID  
• Supports multiple UUIDs at once  
• Outputs rows sorted by IND  

──────────────────────────────────────────────  
🧩 UPDATE TOOL  
──────────────────────────────────────────────  

• Updates fields at given INDs  
• Supports "IND": "new_n" to insert grouped new rows  
• Groups all fields with the same "new_n" into one row  

──────────────────────────────────────────────  
🧩 DELETE TOOL  
──────────────────────────────────────────────  

• Deletes:  
 → Specific rows (by table + IND)  
 → All rows (where = ["all"])  
• Deletes from Registry when all tables are targeted  
• Does not allow targeting "Registry" directly  

──────────────────────────────────────────────  
END OF USER MANUAL  
──────────────────────────────────────────────
