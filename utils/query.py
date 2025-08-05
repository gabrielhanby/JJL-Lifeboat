import threading
import copy

# Runtime buffer and timer state
request_buffer = {}
request_counter = 0
dispatch_timer = None
timer_lock = threading.Lock()

# Shared state (set via initialize)
conn = None
cursor = None
db_meta = None
tools = {}

# Store last results per process/tool
last_results = {}

# Timer handler
def _start_dispatch_timer():
    global dispatch_timer
    with timer_lock:
        if dispatch_timer:
            dispatch_timer.cancel()
        dispatch_timer = threading.Timer(3.0, _dispatch_requests)
        dispatch_timer.start()

# Submit a new request (from CLI or test)
def submit_request(pkg: dict):
    global request_counter
    request_counter += 1
    request_id = f"request_{request_counter}"
    request_buffer[request_id] = pkg
    _start_dispatch_timer()

# Dispatch after timer expires
def _dispatch_requests():
    global last_results
    if not request_buffer:
        return

    buffered = copy.deepcopy(request_buffer)
    request_buffer.clear()
    last_results = {}

    # Merge all incoming packages into process_n blocks
    process_n = {}
    process_counter = 0

    for request in buffered.values():
        for process_key, content in request.items():
            if not process_key.startswith("process_"):
                process_counter += 1
                process_key = f"process_{process_counter}"
            if process_key not in process_n:
                process_n[process_key] = {
                    "create": {},
                    "update": {},
                    "delete": {},
                    "read": {"UUID": []},
                    "search": {}
                }

            for tool, tool_data in content.items():
                if tool == "create":
                    process_n[process_key]["create"].update(tool_data)
                elif tool == "update":
                    process_n[process_key]["update"].update(tool_data)
                elif tool == "delete":
                    process_n[process_key]["delete"].update(tool_data)
                elif tool == "read":
                    uuids = tool_data.get("UUID", [])
                    if isinstance(uuids, list):
                        process_n[process_key]["read"]["UUID"].extend(uuids)
                    else:
                        process_n[process_key]["read"]["UUID"].append(uuids)
                elif tool == "search":
                    process_n[process_key]["search"].update(tool_data)

    # Dispatch each process independently
    for process_key, tools_block in process_n.items():
        for tool in ["create", "update", "delete", "read", "search"]:
            tool_data = tools_block.get(tool)
            if tool_data and tool in tools:
                result = tools[tool](tool_data, conn, cursor, db_meta)
                last_results[f"{process_key}_{tool}"] = result

    # Commit any writes after all processes run
    if conn:
        conn.commit()

# Get last dispatch results
def get_last_results():
    return last_results

# One-time initialization from CLI/test
def initialize(tool_handlers: dict, live_conn, live_cursor, meta):
    global tools, conn, cursor, db_meta
    tools = tool_handlers
    conn = live_conn
    cursor = live_cursor
    db_meta = meta
