def handle(package: dict, conn, cursor, db_meta) -> dict:
    result = {
        "status": "success",
        "errors": [],
        "action": {}
    }

    try:
        uuids = package.get("UUID", [])
        tables = [t for t in db_meta["tables"] if t not in ("Registry", "sqlite_sequence")]

        for uuid in uuids:
            result["action"][uuid] = {}

            for table in tables:
                fields = db_meta["fields"][db_meta["tables"].index(table)]
                sql = f"SELECT {', '.join(fields)} FROM {table} WHERE UUID = ? ORDER BY IND ASC"
                cursor.execute(sql, (uuid,))
                rows = cursor.fetchall()

                if rows:
                    result["action"][uuid][table] = {
                        "fields": fields,
                        "rows": rows
                    }

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))

    return result
