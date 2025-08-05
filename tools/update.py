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

            # Flatten field names to check existence
            if field_list and isinstance(field_list[0], list):
                flattened_fields = set()
                for sublist in field_list:
                    flattened_fields.update(sublist)
            else:
                flattened_fields = set(field_list)

            missing = [f for f in flattened_fields if f not in fields[table]]
            if missing:
                result["errors"].append(f"Missing fields in '{table}': {missing}")
                continue

            insert_rows = {}
            update_count = 0
            insert_count = 0

            for fields_sub, ind_sub, values_sub in zip(field_list, ind_list, value_list):
                if isinstance(ind_sub, str) and ind_sub.startswith("new"):
                    insert_rows.setdefault(ind_sub, []).append((fields_sub, values_sub))
                else:
                    # Defensive fix: ensure fields_sub is list
                    if isinstance(fields_sub, str):
                        fields_sub = [fields_sub]

                    # Defensive fix: ensure values_sub is list
                    if isinstance(values_sub, str):
                        values_sub = [values_sub]

                    set_clause = ", ".join(f"{f} = ?" for f in fields_sub)
                    sql = f"UPDATE {table} SET {set_clause} WHERE UUID = ? AND IND = ?"
                    cursor.execute(sql, (*values_sub, uuid_key, int(ind_sub)))
                    update_count += 1

            # Process inserts grouped by new_n key
            for _, field_groups in insert_rows.items():
                cursor.execute(f"SELECT MAX(IND) FROM {table} WHERE UUID = ?", (uuid_key,))
                max_ind = cursor.fetchone()[0]
                next_ind = (max_ind + 1) if max_ind is not None else 0

                merged_fields = []
                merged_values = []
                for f_set, v_set in field_groups:
                    if isinstance(f_set, str):
                        merged_fields.append(f_set)
                    else:
                        merged_fields.extend(f_set)

                    if isinstance(v_set, str):
                        merged_values.append(v_set)
                    else:
                        merged_values.extend(v_set)

                placeholders = ", ".join("?" for _ in merged_fields)
                field_str = ", ".join(["UUID", "IND"] + merged_fields)
                sql = f"INSERT INTO {table} ({field_str}) VALUES ({', '.join(['?'] * (2 + len(merged_fields)))})"
                row = [uuid_key, next_ind] + merged_values
                cursor.execute(sql, row)
                insert_count += 1

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
