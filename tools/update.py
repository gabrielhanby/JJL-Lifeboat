def handle(package, conn, cursor, db_meta):
    result = {
        "status": "success",
        "errors": [],
        "action": {
            "updates": {},
            "inserts": {}
        }
    }

    tables = db_meta["tables"]
    fields = {table: set(cols) for table, cols in zip(tables, db_meta["fields"])}

    for uuid_key, data in package.items():
        for table, field_list, ind_list, value_list in zip(
            data["table"], data["field"], data["IND"], data["value"]
        ):
            if table not in tables:
                result["errors"].append(f"Table '{table}' does not exist.")
                continue

            # Flatten to check for missing fields
            all_fields = []
            for f in field_list:
                all_fields.extend(f if isinstance(f, list) else [f])

            missing = [f for f in all_fields if f not in fields[table]]
            if missing:
                result["errors"].append(f"Missing fields in '{table}': {missing}")
                continue

            insert_groups = {}
            update_count = 0
            insert_count = 0

            for fields_sub, ind_sub, values_sub in zip(field_list, ind_list, value_list):
                if isinstance(ind_sub, str) and ind_sub.startswith("new"):
                    insert_groups.setdefault(ind_sub, []).append((fields_sub, values_sub))
                else:
                    if isinstance(fields_sub, str):
                        fields_sub = [fields_sub]
                    if isinstance(values_sub, str):
                        values_sub = [values_sub]

                    try:
                        set_clause = ", ".join(f"{f} = ?" for f in fields_sub)
                        sql = f"UPDATE {table} SET {set_clause} WHERE UUID = ? AND IND = ?"
                        cursor.execute(sql, (*values_sub, uuid_key, int(ind_sub)))
                        update_count += cursor.rowcount
                    except Exception as e:
                        result["errors"].append(f"{table}[{uuid_key}, IND {ind_sub}]: {str(e)}")

            for _, field_value_list in insert_groups.items():
                try:
                    cursor.execute(f"SELECT MAX(IND) FROM {table} WHERE UUID = ?", (uuid_key,))
                    max_ind = cursor.fetchone()[0]
                    next_ind = (max_ind + 1) if max_ind is not None else 0

                    merged_fields = []
                    merged_values = []
                    for f_set, v_set in field_value_list:
                        merged_fields.extend(f_set if isinstance(f_set, list) else [f_set])
                        merged_values.extend(v_set if isinstance(v_set, list) else [v_set])

                    field_str = ", ".join(["UUID", "IND"] + merged_fields)
                    sql = f"INSERT INTO {table} ({field_str}) VALUES ({', '.join(['?'] * (2 + len(merged_fields)))})"
                    cursor.execute(sql, [uuid_key, next_ind] + merged_values)
                    insert_count += 1

                except Exception as e:
                    result["errors"].append(f"{table}[{uuid_key}, insert]: {str(e)}")

            if update_count:
                result["action"]["updates"][table] = result["action"]["updates"].get(table, 0) + update_count
            if insert_count:
                result["action"]["inserts"][table] = result["action"]["inserts"].get(table, 0) + insert_count

    conn.commit()

    if result["errors"] and not (result["action"]["updates"] or result["action"]["inserts"]):
        result["status"] = "error"
    elif result["errors"]:
        result["status"] = "partial"

    return result
