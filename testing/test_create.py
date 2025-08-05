import time
from utils import query
from utils.connect import conn, cursor, db_meta
from tools import create, read, update, delete

# Initialize query system with tool handlers
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

# Submit one person with contact info and one note
create_package = {
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

# Submit the request
query.submit_request(create_package)

# Wait for 3s timer to trigger dispatch
print("[TEST] Submitted create package. Waiting for dispatch...")
time.sleep(4)
