import json
from utils import connect, batch
from tools import create, update, delete, read, search

def main():
    # Step 1: Get shared environment
    conn, cursor, db_meta = connect.get_env()

    # Step 2: Load all UUIDs from Registry
    cursor.execute("SELECT UUID FROM Registry")
    uuids = [row[0] for row in cursor.fetchall()]

    if not uuids:
        print("[INFO] No UUIDs found to delete.")
        return

    # Step 3: Build delete package
    delete_pkg = {
        "delete": {
            uuid: {
                "where": ["all"],
                "IND": [""]
            }
            for uuid in uuids
        }
    }

    package = {
        "batch_1": {
            "process_1": delete_pkg
        }
    }

    # Step 4: Define tool handlers
    tool_handlers = {
        "create": create.handle,
        "update": update.handle,
        "delete": delete.handle,
        "read": read.handle,
        "search": search.handle
    }

    # Step 5: Run batch
    result = batch.handle_batch(package, conn, cursor, db_meta, tool_handlers)

    # Step 6: Pretty print result
    print("\n🗑️ Delete All Result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
