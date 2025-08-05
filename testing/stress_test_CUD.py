import time
from utils import query
from utils.connect import conn, cursor, db_meta
from tools import create, read, update, delete
from pprint import pprint

def main():
    query.initialize(
        {
            "create": create.handle,
            "read": read.handle,
            "update": update.handle,
            "delete": delete.handle
        },
        conn,
        cursor,
        db_meta
    )

    uuid = "1ef984e3-321b-402b-99ea-2f14d147fefc"

    # Submit delete package
    delete_pkg = {
        "delete": {
            uuid: {"where": ["all"], "IND": [""]}
        }
    }
    print("[TEST] Submitting DELETE package...")
    query.submit_request(delete_pkg)
    time.sleep(1)  # Wait for query to buffer

    # Submit update package
    update_pkg = {
        "update": {
            uuid: {
                "table": ["Contacts"],
                "field": [["first_name"]],
                "IND": [[0]],
                "value": [["Test"]]
            }
        }
    }
    print("[TEST] Submitting UPDATE package...")
    query.submit_request(update_pkg)
    time.sleep(1)  # Wait for query to buffer

    # Submit create package
    create_pkg = {
        "create": {
            "group_1": {
                "table": ["Contacts", "Notes"],
                "field": [
                    ["first_name", "last_name"],
                    ["subject", "body"]
                ],
                "value": [
                    ["John", "Locke"],
                    ["Stress Note", "success"]
                ]
            }
        }
    }
    print("[TEST] Submitting CREATE package...")
    query.submit_request(create_pkg)

    # Wait enough time for the query timer to expire and dispatch all at once
    time.sleep(4)

    # Fetch all results once
    all_results = query.get_last_results()

    # Print results in tool order
    for tool in ["create", "update", "delete"]:
        print(f"[{tool.upper()} RESULT]")
        pprint(all_results.get(tool, {}))

if __name__ == "__main__":
    main()
