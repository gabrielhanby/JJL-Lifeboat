import time
from utils import query
from utils.connect import conn, cursor, db_meta
from tools import create, read, update, delete

# Initialize query system
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

# Build delete package
delete_package = {
    "delete": {
        "0823fc12-ad4a-4654-87e7-9c90d8f7c6bd": {
            "where": ["all"],
            "IND": [0]
        }
    }
}

# Submit the request
query.submit_request(delete_package)

print("[TEST] Submitted delete package. Waiting for dispatch...")
time.sleep(4)
