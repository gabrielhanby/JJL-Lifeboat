from utils.connect import conn, cursor, db_meta
from utils.batch import handle_batch
from tools import read

# Tool dispatch mapping
tool_handlers = {
    "read": read.handle
}

# Read package — pulls all data from all tables for a given UUID
read_package = {
    "batch_1": {
        "process_1": {
            "read": {
                "UUID": [
                    "842f8eac-8db3-47e4-a4b2-a9a9b57b771e"
                ]
            }
        }
    }
}

# Run the batch handler
result = handle_batch(read_package, conn, cursor, db_meta, tool_handlers)

# Print output
print("\n📚 READ RESULT:")
print("Status:", result.get("status"))

if result.get("status") != "success":
    print("❌ Errors:", result.get("errors", []))
else:
    action = result.get("action", {})
    for uuid, tables in action.items():
        print(f"\n🆔 UUID: {uuid}")
        for table, data in tables.items():
            print(f"  📄 Table: {table}")
            print(f"    Fields: {', '.join(data['fields'])}")
            for row in data["rows"]:
                print(f"    → {row}")
