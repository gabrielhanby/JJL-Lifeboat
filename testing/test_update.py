import time
from utils import query
from utils.connect import conn, cursor, db_meta
from tools import create, read, update, delete
from pprint import pprint

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

update_package = {
    "update": {
        "3e641018-e2c6-4f32-be82-9ada65af7c26": {
            "table": ["Contacts"],
            "field": [["first_name"]],
            "IND": [[0]],
            "value": [["Gabriel"]]
        }
    }
}

query.submit_request(update_package)

print("[TEST] Submitted update package. Waiting for dispatch...")
time.sleep(4)

result = query.get_last_results()
print("\n[UPDATE RESULT]")
pprint(result.get("update", {}))
