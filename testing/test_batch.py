import json
from utils import connect, batch
from tools import create, update, delete, read, search

def main():
    # Step 1: Get shared environment
    conn, cursor, db_meta = connect.get_env()

    # Step 2: Build CUD test package
    package = {
        "batch_1": {
            "process_1": {
                "create": {
                    "group_1": {
                        "table": ["Contacts", "Notes"],
                        "field": [
                            ["first_name", "middle_name", "last_name"],
                            ["subject", "body"]
                        ],
                        "value": [
                            [["John", "Doe", "Lock"]],
                            [["Test Results", "Test Successful"]]
                        ]
                    }
                }
            },
            "process_2": {
                "update": {
                    "cfe38ef0-0f21-4593-8a54-f0cfdc4e940b": {
                        "table": ["Contacts", "Notes"],
                        "field": [
                            ["first_name"],
                            ["subject", "body"]
                        ],
                        "IND": [
                            [0],
                            ["new_1", "new_1"]
                        ],
                        "value": [
                            ["Gabriel"],
                            ["Batch Edit Note", "Batch Edit Successful"]
                        ]
                    }
                }
            }
        }
    }

    # Step 3: Define tool handlers
    tool_handlers = {
        "create": create.handle,
        "update": update.handle,
        "delete": delete.handle,
        "read": read.handle,
        "search": search.handle
    }

    # Step 4: Send to batch
    result = batch.handle_batch(package, conn, cursor, db_meta, tool_handlers)

    # Step 5: Pretty print result
    print("\n📦 Batch Result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
