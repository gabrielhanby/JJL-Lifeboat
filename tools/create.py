import uuid

def handle(package, conn, cursor, db_meta):
    result = {
        "status": "success",
        "errors": [],
        "action": {
            "created": [],
            "inserts": {}
        }
    }

    tables = db_meta["tables"]
    fields = {table: set(cols) for table, cols in zip(tables, db_meta["fields"])}

    for group_name, group_data in package.items():
        try:
            new_uuid = str(uuid.uuid4())
            result["action"]["created"].append(new_uuid)

            for table, field_list, value_list in zip(
                group_data["table"],
                group_data["field"],
                group_data["value"]
            ):
                if table not in tables:
                    result["errors"].append(f"Table '{table}' does not exist.")
                    continue

                missing = [f for f in field_list if f not in fields[table]]
                if missing:
                    result["errors"].append(f"Missing fields in '{table}': {missing}")
                    continue

                # Ensure value_list is list of lists
                if value_list and isinstance(value_list[0], (str, int, float)):
                    value_list = [value_list]

                cursor.execute(f"SELECT MAX(IND) FROM {table} WHERE UUID = ?", (new_uuid,))
                max_ind = cursor.fetchone()[0]
                next_ind = (max_ind + 1) if max_ind is not None else 0

                placeholders = ", ".join("?" for _ in field_list)
                field_str = ", ".join(["UUID", "IND"] + field_list)
                sql = f"INSERT INTO {table} ({field_str}) VALUES ({', '.join(['?'] * (2 + len(field_list)))})"

                insert_count = 0
                for values in value_list:
                    row = [new_uuid, next_ind] + values
                    cursor.execute(sql, row)
                    next_ind += 1
                    insert_count += 1

                result["action"]["inserts"][table] = result["action"]["inserts"].get(table, 0) + insert_count

            cursor.execute("INSERT INTO Registry (UUID) VALUES (?);", (new_uuid,))

        except Exception as e:
            result["errors"].append(str(e))
            result["status"] = "partial"

    conn.commit()
    if result["errors"] and result["status"] != "partial":
        result["status"] = "error"

    return result
