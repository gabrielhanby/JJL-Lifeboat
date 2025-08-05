from utils import connect, query
from tools import search

# Initialize the query system with tools (only search for this test)
query.initialize(
    tool_handlers={"search": search.search_package},
    live_conn=connect.conn,
    live_cursor=connect.cursor,
    meta=connect.db_meta
)

# Define the test search package
package = {
    "process_1": {
        "search": {
            "Contacts": {
                "first_name": {
                    "and": [{ "equals": "John" }]
                }
            },
            "Notes": {
                "subject": {
                    "and": [{ "equals": "Stress Note" }]
                },
                "body": {
                    "and": [{ "contains": "success" }]
                }
            }
        }
    }
}

# Submit the request
query.submit_request(package)

# Wait a bit to let the timer dispatch (you can skip this if running directly)
import time
time.sleep(3.5)

# Fetch and print the result
results = query.get_last_results()
print("Search result UUIDs:", results.get("process_1_search", []))
