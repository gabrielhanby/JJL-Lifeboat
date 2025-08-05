from utils import connect
from tools import create, read, update, delete
from utils import query
import time
from pprint import pprint

def main():
    # Initialize query with tools and DB connection
    query.initialize(
        tool_handlers={
            "create": create.handle,
            "read": read.handle,
            "update": update.handle,
            "delete": delete.handle
        },
        live_conn=connect.conn,
        live_cursor=connect.cursor,
        meta=connect.db_meta
    )

    package = {
        "read": {
            "UUID": ["0823fc12-ad4a-4654-87e7-9c90d8f7c6bd"]
        }
    }

    print("[TEST_READ] Submitting read request...")
    query.submit_request(package)

    time.sleep(4)  # wait for dispatch

    result = query.get_last_results()
    print("\n[READ RESULT]")
    pprint(result.get("read", {}))

if __name__ == "__main__":
    main()
