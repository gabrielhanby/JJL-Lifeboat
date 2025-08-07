# testing/test_search_stress.py

from utils.connect import conn, cursor, db_meta
from utils.batch import handle_batch
from tools import search

# Tool dispatch mapping
tool_handlers = {
    "search": search.handle
}

# 🔬 Stress test package with deep field logic across multiple tables
search_package = {
    "batch_1": {
        "process_1": {
            "search": {
                "Tracking": {
                    "state_filed": {
                        "and": [{"equals": "TX"}],
                        "or": [{"equals": "AZ"}]
                    },
                    "entity_type": {
                        "and": [{"equals": "Lead"}]
                    },
                    "tags": {
                        "nand": [{"contains": "new"}]
                    }
                },
                "Contacts": {
                    "first_name": {
                        "or": [{"contains": "Ali"}, {"equals": "Charlie"}]
                    },
                    "gender": {
                        "and": [{"equals": "female"}]
                    },
                    "prefix": {
                        "and": [{"is_null": True}]
                    }
                },
                "Notes": {
                    "subject": {
                        "and": [{"contains": "Cher"}],
                        "or": [{"contains": "Love Hurts"}]
                    }
                },
                "Addresses": {
                    "state": {
                        "and": [{"equals": "TX"}],
                        "or": [{"equals": "CA"}]
                    },
                    "city": {
                        "or": [{"contains": "Dallas"}, {"equals": "Phoenix"}]
                    }
                }
            }
        }
    }
}

# 🧪 Execute batch search
result = handle_batch(search_package, conn, cursor, db_meta, tool_handlers)

# 📦 Print results
print("\n🔍 SEARCH RESULT:")
print("Status:", result.get("status"))

if result.get("status") != "success":
    print("❌ Errors:", result.get("errors", []))
else:
    matches = result["action"].get("matches")
    if isinstance(matches, list) and matches:
        print(f"✅ {len(matches)} match(es) found:")
        for uuid in matches:
            print("→", uuid)
    elif isinstance(matches, list):
        print("No matches found in 'matches' key.")
    else:
        print("⚠️ Unexpected format for 'matches':", matches)
