from utils.connect import conn, cursor, db_meta
from utils.batch import handle_batch
from tools import search

# Tool dispatch mapping
tool_handlers = {
    "search": search.handle
}

# Search package — looks for rows in Tracking where state_filed equals 'TX'
search_package = {
    "batch_1": {
        "process_1": {
            "search": {
                "Tracking": {
                    "state_filed": {
                        "and": [{"contains": "TX"}]
                    }
                }
            }
        }
    }
}

# Run the batch handler
result = handle_batch(search_package, conn, cursor, db_meta, tool_handlers)

# Show only results
print("\n🔍 SEARCH RESULT:")
matches = result["action"].get("matches")

if isinstance(matches, list) and matches:
    print(f"✅ {len(matches)} match(es) found:")
    for uuid in matches:
        print("→", uuid)
elif isinstance(matches, list):
    print("No matches found.")
else:
    print("⚠️ Unexpected format for 'matches':", matches)
