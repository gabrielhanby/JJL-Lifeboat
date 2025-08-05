def handle(package, conn, cursor, db_meta):
    requested_uuids = package.get("UUID", [])
    if isinstance(requested_uuids, str):
        requested_uuids = [requested_uuids]

    tables = db_meta["tables"]
    result_data = {}
    errors = []

    for uuid in requested_uuids:
        result_data[uuid] = {}

        for table in tables:
            if table in ("sqlite_sequence", "Registry"):
                continue

            try:
                cursor.execute(f"SELECT * FROM {table} WHERE UUID = ? ORDER BY IND ASC;", (uuid,))
                rows = cursor.fetchall()
                col_names = [desc[0] for desc in cursor.description]
                row_dicts = [dict(zip(col_names, row)) for row in rows]
                result_data[uuid][table] = row_dicts

            except Exception as e:
                result_data[uuid][table] = []
                errors.append(f"Error querying {table} for UUID {uuid}: {str(e)}")

    status = "success"
    if errors:
        status = "partial" if result_data else "error"

    return {
        "status": status,
        "errors": errors,
        "action": {
            "results": result_data
        }
    }
