def handle(package, conn, cursor, db_meta):
    result = {
        "status": "success",
        "errors": [],
        "action": {
            "results": {}
        }
    }

    requested_uuids = package.get("UUID", [])
    if isinstance(requested_uuids, str):
        requested_uuids = [requested_uuids]

    tables = db_meta["tables"]

    for uuid in requested_uuids:
        result["action"]["results"][uuid] = {}

        for table in tables:
            if table in ("sqlite_sequence", "Registry"):
                continue

            try:
                cursor.execute(f"SELECT * FROM {table} WHERE UUID = ? ORDER BY IND ASC;", (uuid,))
                rows = cursor.fetchall()
                col_names = [desc[0] for desc in cursor.description]
                row_dicts = [dict(zip(col_names, row)) for row in rows]
                result["action"]["results"][uuid][table] = row_dicts
            except Exception as e:
                result["errors"].append(f"{table}[{uuid}]: {str(e)}")
                result["action"]["results"][uuid][table] = []

    if result["errors"] and not result["action"]["results"]:
        result["status"] = "error"
    elif result["errors"]:
        result["status"] = "partial"

    return result
