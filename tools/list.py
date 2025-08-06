def handle(package: dict, conn, cursor, db_meta) -> dict:
    result = {
        "status": "success",
        "errors": [],
        "action": {}
    }

    try:
        UUID = package.get("UUID")
        tables = package.get("table", [])

        if not UUID:
            result["status"] = "error"
            result["errors"].append("UUID is required in the list package.")
            return result

        # Determine which tables to query
        if not tables or tables == ["all"]:
            valid_tables = [t for t in db_meta["tables"] if t not in ("Registry", "sqlite_sequence")]
        else:
            valid_tables = [t for t in tables if t in db_meta["tables"] and t not in ("Registry", "sqlite_sequence")]

        for table in valid_tables:
            fields = db_meta["fields"][db_meta["tables"].index(table)]
            sql = f"SELECT * FROM {table} WHERE UUID = ? ORDER BY IND ASC"
            cursor.execute(sql, (UUID,))
            rows = cursor.fetchall()

            # Store results under the table name
            result["action"][table] = {
                "fields": fields,
                "rows": [list(row) for row in rows]
            }

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
        result["action"] = {}

    return result
