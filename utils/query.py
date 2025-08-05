import threading
import copy

# Runtime buffer and timer state
request_buffer = {}
request_counter = 0
dispatch_timer = None
timer_lock = threading.Lock()

# References to shared state (set via initialize)
conn = None
cursor = None
db_meta = None
tools = {}

# Store last results from dispatch
last_results = {}

# Timer thread handler
def _start_dispatch_timer():
    global dispatch_timer
    with timer_lock:
        if dispatch_timer:
            dispatch_timer.cancel()
        dispatch_timer = threading.Timer(3.0, _dispatch_requests)
        dispatch_timer.start()

# External API for submitting packages
def submit_request(pkg: dict):
    global request_counter
    request_counter += 1
    request_id = f"request_{request_counter}"
    request_buffer[request_id] = pkg
    _start_dispatch_timer()

# Internal: dispatch logic after timer expires
def _dispatch_requests():
    global last_results
    if not request_buffer:
        return

    buffered = copy.deepcopy(request_buffer)
    request_buffer.clear()

    # Initialize grouped packages per tool
    grouped = {
        "create": {},
        "read": {"UUID": []},
        "update": {},
        "delete": {}
    }

    # Merge requests by tool
    for request in buffered.values():
        for tool, content in request.items():
            if tool == "create":
                grouped["create"].update(content)
            elif tool == "read":
                uuids = content.get("UUID")
                if isinstance(uuids, list):
                    grouped["read"]["UUID"].extend(uuids)
                else:
                    grouped["read"]["UUID"].append(uuids)
            elif tool == "update":
                grouped["update"].update(content)
            elif tool == "delete":
                grouped["delete"].update(content)

    last_results = {}

    # Dispatch tools synchronously in fixed order
    for tool in ["create", "update", "delete", "read"]:
        clumped_pkg = grouped.get(tool)
        if clumped_pkg and tool in tools:
            # Call the tool handler with its merged package
            last_results[tool] = tools[tool](clumped_pkg, conn, cursor, db_meta)

    # Commit once after all write operations
    if conn:
        conn.commit()

# External: fetch last dispatched results
def get_last_results():
    return last_results

# One-time setup from CLI or main runner
def initialize(tool_handlers: dict, live_conn, live_cursor, meta):
    global tools, conn, cursor, db_meta
    tools = tool_handlers
    conn = live_conn
    cursor = live_cursor
    db_meta = meta
