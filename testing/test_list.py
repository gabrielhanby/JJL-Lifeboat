from utils.connect import conn, cursor, db_meta
from utils.batch import handle_batch
from tools import list as list_tool

# Tool dispatcher
tool_handlers = {
    "list": list_tool.handle
}

# List package to show all tables for the specified UUID
list_package = {
    "batch_1": {
        "process_1": {
            "list": {
                "UUID": "842f8eac-8db3-47e4-a4b2-a9a9b57b771e",
                "table": ["Contacts"]
            }
        }
    }
}

# Run it
result = handle_batch(list_package, conn, cursor, db_meta, tool_handlers)

# Output results
print("\n📋 LIST RESULT:")
print("Status:", result.get("status"))

if result.get("status") != "success":
    print("❌ Errors:", result.get("errors", []))
else:
    for table, data in result["action"].items():
        print(f"\n🗂️ Table: {table}")
        fields = data.get("fields", [])
        rows = data.get("rows", [])
        print("  Fields:", ", ".join(fields))

        if not rows:
            print("  No rows found.")
        else:
            for row in rows:
                print("  →", row)
