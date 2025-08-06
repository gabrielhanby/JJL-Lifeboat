import copy

def is_valid_data(d):
    if not isinstance(d, dict) or not d:
        return False
    for v in d.values():
        if isinstance(v, dict):
            if is_valid_data(v):
                return True
        elif isinstance(v, list):
            if v:
                return True
        elif v not in ("", None):
            return True
    return False

def handle_batch(raw_package: dict, conn, cursor, db_meta, tool_handlers: dict):
    batch_result = {
        "status": "success",
        "errors": [],
        "action": {}
    }

    for batch_key, batch in raw_package.items():
        reorganized = {
            "create": {},
            "update": {},
            "delete": {}
        }
        group_counter = 1

        for process in batch.values():
            for tool, tool_data in process.items():
                if not is_valid_data(tool_data):
                    continue

                # ──────────────────────────────
                # 🧪 Passthrough tools: read/search
                # ──────────────────────────────
                if tool not in ("create", "update", "delete"):
                    try:
                        output = tool_handlers[tool](tool_data, conn, cursor, db_meta)

                        # 🧩 Only merge the actual action output (flattened)
                        batch_result["action"].update(output.get("action", {}))

                        if output.get("status") in ("error", "partial"):
                            batch_result["status"] = "partial" if batch_result["status"] == "success" else "error"
                            batch_result["errors"].extend(output.get("errors", []))

                    except Exception as e:
                        batch_result["status"] = "error"
                        err_msg = f"{tool} failed: {str(e)}"
                        batch_result["errors"].append(err_msg)

                    continue

                # ──────────────────────────────
                # CUD Tools
                # ──────────────────────────────
                if tool == "create":
                    for _, group in tool_data.items():
                        group_id = f"group_{group_counter}"
                        reorganized["create"][group_id] = group
                        group_counter += 1
                elif tool in ("update", "delete"):
                    reorganized[tool].update(tool_data)

        # ──────────────────────────────
        # Run C → U → D in order
        # ──────────────────────────────
        for tool in ["create", "update", "delete"]:
            if reorganized[tool] and tool in tool_handlers:
                try:
                    output = tool_handlers[tool](reorganized[tool], conn, cursor, db_meta)
                    wrapped = {
                        "status": output.get("status", "unknown"),
                        "errors": output.get("errors", []),
                        "action": output.get("action", {})
                    }
                    batch_result["action"][tool] = wrapped

                    if wrapped["status"] in ("error", "partial"):
                        batch_result["status"] = "partial" if batch_result["status"] == "success" else "error"
                        batch_result["errors"].extend(wrapped["errors"])

                except Exception as e:
                    batch_result["status"] = "error"
                    err_msg = f"{tool} failed: {str(e)}"
                    batch_result["errors"].append(err_msg)
                    batch_result["action"][tool] = {
                        "status": "error",
                        "errors": [err_msg],
                        "action": {}
                    }

    if conn:
        conn.commit()

    return batch_result
