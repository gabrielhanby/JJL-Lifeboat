🧾 Carpathia CLI – System User Manual

──────────────────────────────────────────────  
🧠 SYSTEM RULES & DESIGN  
──────────────────────────────────────────────  

• Every table (except Registry and sqlite_sequence) must include:  
  - UUID (unique per entity, primary key)  
  - IND (index per UUID starting at 0)

• A `Registry` table must exist:
  - Contains only `UUID` as primary key
  - Tracks all created UUIDs

• `sqlite_sequence` and `Registry` are the only tables exempt from UUID/IND rules.

• Tools are executed in strict order:  
  **create → update → delete**

• Tools receive a standardized package and return an action/status/result triplet.

──────────────────────────────────────────────  
🖥️ CLI DESIGN: Ladders & Layers  
──────────────────────────────────────────────  

The CLI UI is composed of:
• **Header** – Displays system name, commands, ladder view, last command/output.
• **Ladder** – Stack of layers; each layer is a screen (tool or UI component).
• **Active Layer** – The current page you’re interacting with.

Ladder behavior:
- Layers only appear in the ladder after first use.
- You can navigate with `back`, `forth`, `home`, or call any layer directly.
- Layer calls insert the target layer just above the active one and set it as active.
- `back` moves -1 index, `forth` moves +1 index.
- `home` moves the Home layer to the top and activates it.
- `exit` while in Home prompts to close the CLI (y/n).
- `exit all` prompts to close from any screen.

──────────────────────────────────────────────  
📁 PROJECT TREE STRUCTURE  
──────────────────────────────────────────────  

/ (project root)
├─ CLI/
│  ├─ src/
│  │  ├─ main.py         # Entry point
│  │  └─ ladder.py       # Manages ladder logic
│  ├─ layers/            # Tool layer logic
│  ├─ ui/                # Header, prompts, prints
│  └─ state/             # Memory (ladder, last command/output)
├─ tools/                # Tool implementations
├─ utils/                # Core environment + batch logic
│  ├─ connect.py         # Schema + DB validator
│  └─ batch.py           # Reorganizes + dispatches tools
├─ settings/
│  └─ database.json      # Maps database names to paths
├─ testing/
│  ├─ test_create.py     # Test tools manually
│  └─ generate_database.py
├─ data/                 # Active database files
│  └─ docket.db
├─ output/               # CLI log/output

──────────────────────────────────────────────  
📦 MASTER PACKAGE FORMAT  
──────────────────────────────────────────────  

{
  "batch_1": {
    "process_1": {
      "create": { ... },
      "update": { ... },
      "delete": { ... }
    },
    "process_2": {
      "create": { ... }
    }
  }
}

- Sent to: utils/batch.py
- Validated: all inner dicts must contain usable data
- Reorganized:
  - All create → group_n merged
  - All update/delete UUIDs merged
- Read/search/list tools are passed through immediately, not grouped

──────────────────────────────────────────────  
🛠️ ENVIRONMENT – connect.py  
──────────────────────────────────────────────  

Path: utils/connect.py

• Loads settings/database.json
• Validates:
  - Registry table must exist and contain only UUID
  - All other tables must include UUID and IND
• Outputs:
  - conn     → SQLite connection (check_same_thread=False)
  - cursor   → Shared cursor
  - db_meta  → { "tables": [...], "fields": [[...], [...]] }

──────────────────────────────────────────────  
📦 TOOL PACKAGE FORMATS  
──────────────────────────────────────────────  

✅ CREATE  
{
  "process_1": {
    "create": {
      "group_1": {
        "_UUID": "optional-fixed-uuid",
        "table": ["Contacts", "Notes"],
        "field": [
          ["first_name", "last_name"],
          ["subject", "body"]
        ],
        "value": [
          [["Jane", "Smith"]],
          [["Welcome", "Note content"]]
        ]
      }
    }
  }
}

✅ UPDATE  
{
  "process_1": {
    "update": {
      "uuid_1": {
        "table": ["Contacts", "Notes"],
        "field": [["first_name"], ["subject", "body"]],
        "IND": [[0], ["new_1", "new_1"]],
        "value": [["Gabe"], ["New Subject", "Updated note"]]
      }
    }
  }
}

✅ DELETE  
{
  "process_1": {
    "delete": {
      "uuid_1": {
        "where": ["Contacts"],
        "IND": [0]
      },
      "uuid_2": {
        "where": ["all"],
        "IND": [""]
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

✅ SEARCH  
{
  "process_1": {
    "search": {
      "Contacts": {
        "first_name": {
          "and": [{ "equals": "John" }],
          "or": [{ "contains": "Jon" }]
        }
      },
      "Notes": {
        "subject": {
          "and": [{ "equals": "Stress Note" }]
        }
      }
    }
  }
}

──────────────────────────────────────────────  
✅ TOOL RETURN FORMAT  
──────────────────────────────────────────────  

Each tool returns:
{
  "status": "success" | "partial" | "error",
  "errors": [...],
  "action": { ... }
}

✔ CREATE  
{ "created": [...], "inserts": { "Contacts": 2 } }

✔ UPDATE  
{ "updates": { "Contacts": 1 }, "inserts": { "Notes": 1 } }

✔ DELETE  
{ "deleted_rows": { "Contacts": 2 }, "removed_uuids": ["uuid_2"] }

✔ READ  
{ "results": { "uuid_1": { "Contacts": [...], "Notes": [...] } } }

✔ SEARCH  
{ "matches": ["uuid_1", "uuid_2"] }

──────────────────────────────────────────────  
🧰 HOW TO RUN  
──────────────────────────────────────────────  

1. CLI or script calls connect.py → opens conn, cursor, db_meta.
2. CLI builds a batch-formatted package.
3. Package sent to utils/batch.py.
4. batch.py:
   - Validates data
   - Reorganizes write tools
   - Dispatches tools in correct order
   - Collects and returns merged result
5. Output shown via CLI HUD (or printed by script)

──────────────────────────────────────────────  
END OF MANUAL  
──────────────────────────────────────────────
