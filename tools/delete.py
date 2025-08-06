def reindex_inds_for_uuid(conn, cursor, table, uuid):
    cursor.execute(f"SELECT rowid FROM {table} WHERE UUID = ? ORDER BY IND ASC;", (uuid,))
    rows = cursor.fetchall()
    for new_ind, (rowid,) in enumerate(rows):
        cursor.execute(f"UPDATE {table} SET IND = ? WHERE rowid = ?;", (new_ind, rowid))

def handle(package, conn, cursor, db_meta):
    result = {
        "status": "success",
        "errors": [],
        "action": {
            "deleted_rows": {},
            "removed_uuids": []
        }
    }

    tables = db_meta["tables"]
    affected = {}  # Track UUIDs that need reindexing per table

    for uuid_key, data in package.items():
        where_list = data.get("where", [])
        ind_list = data.get("IND", [])

        if where_list == ["all"]:
            for table in tables:
                if table in ("sqlite_sequence", "Registry"):
                    continue

                try:
                    cursor.execute(f"DELETE FROM {table} WHERE UUID = ?", (uuid_key,))
                    count = cursor.rowcount
                    if count > 0:
                        result["action"]["deleted_rows"][table] = result["action"]["deleted_rows"].get(table, 0) + count
                        affected.setdefault(table, set()).add(uuid_key)
                except Exception as e:
                    result["errors"].append(f"{table}[{uuid_key}]: {str(e)}")

            try:
                cursor.execute("DELETE FROM Registry WHERE UUID = ?", (uuid_key,))
                if cursor.rowcount:
                    result["action"]["removed_uuids"].append(uuid_key)
            except Exception as e:
                result["errors"].append(f"Registry delete failed for {uuid_key}: {str(e)}")

        else:
            for table_name, ind in zip(where_list, ind_list):
                if table_name in ("Registry", "sqlite_sequence"):
                    result["errors"].append(f"Cannot delete directly from '{table_name}'")
                    continue
                if table_name not in tables:
                    result["errors"].append(f"Table '{table_name}' does not exist")
                    continue

                try:
                    cursor.execute(
                        f"DELETE FROM {table_name} WHERE UUID = ? AND IND = ?",
                        (uuid_key, int(ind))
                    )
                    count = cursor.rowcount
                    if count > 0:
                        result["action"]["deleted_rows"][table_name] = result["action"]["deleted_rows"].get(table_name, 0) + count
                        affected.setdefault(table_name, set()).add(uuid_key)
                except Exception as e:
                    result["errors"].append(f"{table_name}[{uuid_key}, IND {ind}]: {str(e)}")

    for table_name, uuid_set in affected.items():
        for uuid in uuid_set:
            reindex_inds_for_uuid(conn, cursor, table_name, uuid)

    conn.commit()

    if result["errors"] and not (result["action"]["deleted_rows"] or result["action"]["removed_uuids"]):
        result["status"] = "error"
    elif result["errors"]:
        result["status"] = "partial"

    return result
