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
  create → update → delete → read → search  

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
📦 PACKAGE FORMAT PER TOOL  
──────────────────────────────────────────────  

✅ CREATE  
{
  "process_1": {
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
}

✅ READ  
{
  "process_1": {
    "read": {
      "UUID": ["uuid_1", "uuid_2"]
    }
  }
}

✅ UPDATE  
{
  "process_1": {
    "update": {
      "uuid_1": {
        "table": ["Notes"],
        "field": [["subject", "body"]],
        "IND": [["new_1", "new_1"]],
        "value": [["Follow-up", "Another note"]]
      }
    }
  }
}

✅ DELETE  
{
  "process_1": {
    "delete": {
      "uuid_1": {
        "where": ["Notes", "Notes"],
        "IND": ["1", "2"]
      },
      "uuid_2": {
        "where": ["all"],
        "IND": [""]
      }
    }
  }
}

✅ SEARCH  
{
  "process_1": {
    "search": {
      "Contacts": {
        "first_name": {
          "and": [
            { "equals": "John" },
            { "contains": "oh" }
          ],
          "or": [
            { "equals": "Jonathan" },
            { "contains": "Jon" }
          ]
        }
      },
      "Notes": {
        "subject": {
          "and": [{ "equals": "Stress Note" }]
        },
        "body": {
          "or": [{ "contains": "success" }]
        }
      }
    }
  }
}

• Each table defines one or more fields  
• Each field may have:  
  - "and": [ { equals: "..." }, { contains: "..." } ]  
  - "or":  [ { equals: "..." }, { contains: "..." } ]  
• A field passes if either group is satisfied  
• A table passes if all its fields pass  
• Final UUIDs are those found in every matching table (intersection)  

──────────────────────────────────────────────  
🔁 PACKAGE DISPATCH – query.py  
──────────────────────────────────────────────  

Path: ../utils/query.py  

• submit_request(pkg) buffers all packages into process_n blocks  
• 3-second timer resets with every new request  
• When the timer expires:  
  - Each process is dispatched independently  
  - Tool order per process is:  
    1. create  
    2. update  
    3. delete  
    4. read  
    5. search  
• All tools run on shared conn, cursor, db_meta  
• Results are stored in last_results like:  
  {
    "process_1_create": {...},
    "process_1_read": {...},
    "process_2_search": {...}
  }

──────────────────────────────────────────────  
📤 HOW TO SUBMIT A PACKAGE  
──────────────────────────────────────────────  

From CLI or test file:
from utils import query  
query.submit_request({
  "process_1": {
    "create": {...},
    "read": {...}
  },
  "process_2": {
    "search": {...}
  }
})

• The 3-second timer starts on first request  
• If no more requests arrive, the batch is dispatched  

──────────────────────────────────────────────  
✅ TOOL RETURN FORMAT  
──────────────────────────────────────────────  

Each tool returns:
{
  "action": "create" | "update" | "delete" | "read" | "search",
  "status": "success" | "partial" | "error",
  "result": { ... }
}

Tool-specific result content:

✔ CREATE  
{
  "result": {
    "created": [ "uuid_1", "uuid_2" ],
    "inserts": { "Contacts": 3, "Notes": 2 }
  }
}

✔ UPDATE  
{
  "result": {
    "updates": { "Contacts": 1 },
    "inserts": { "Notes": 1 }
  }
}

✔ DELETE  
{
  "result": {
    "deleted_rows": { "Contacts": 2, "Notes": 1 },
    "removed_uuids": [ "uuid_2" ]
  }
}

✔ READ  
{
  "result": {
    "results": {
      "uuid_1": {
        "Contacts": [ ... ],
        "Notes": [ ... ]
      }
    }
  }
}

✔ SEARCH  
{
  "result": [
    "uuid_1",
    "uuid_2"
  ]
}

──────────────────────────────────────────────  
END OF USER MANUAL  
──────────────────────────────────────────────
