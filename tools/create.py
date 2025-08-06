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

    # Step 1: Load existing UUIDs from Registry
    cursor.execute("SELECT UUID FROM Registry")
    existing_uuids = {row[0] for row in cursor.fetchall()}

    tables = db_meta["tables"]
    fields = {table: set(cols) for table, cols in zip(tables, db_meta["fields"])}

    # Step 2: Identify groups needing UUIDs
    uuidless_groups = []
    static_uuid_groups = {}

    for group_name, group_data in package.items():
        if "_UUID" in group_data and group_data["_UUID"]:
            custom_uuid = group_data["_UUID"]
            if custom_uuid in existing_uuids:
                result["errors"].append(f"group '{group_name}': UUID '{custom_uuid}' already exists in Registry.")
                result["status"] = "partial"
                continue
            static_uuid_groups[group_name] = custom_uuid
        else:
            uuidless_groups.append(group_name)

    # Step 3: Generate new UUIDs for uuidless groups
    new_uuids = []
    while len(new_uuids) < len(uuidless_groups):
        candidate = str(uuid.uuid4())
        if candidate not in existing_uuids and candidate not in new_uuids:
            new_uuids.append(candidate)

    # Step 4: Fill back UUIDs into the package
    for group_name, uuid_val in zip(uuidless_groups, new_uuids):
        package[group_name]["_UUID"] = uuid_val
        static_uuid_groups[group_name] = uuid_val

    # Step 5: Process inserts for each group
    for group_name, group_data in package.items():
        if group_name not in static_uuid_groups:
            # Skip invalid UUID groups that failed earlier
            continue

        try:
            uuid_val = static_uuid_groups[group_name]
            result["action"]["created"].append(uuid_val)

            for table, field_list, value_list in zip(
                group_data["table"],
                group_data["field"],
                group_data["value"]
            ):
                if table not in tables:
                    result["errors"].append(f"group '{group_name}': Table '{table}' does not exist.")
                    continue

                missing = [f for f in field_list if f not in fields[table]]
                if missing:
                    result["errors"].append(f"group '{group_name}': Missing fields in '{table}': {missing}")
                    continue

                if value_list and isinstance(value_list[0], (str, int, float)):
                    value_list = [value_list]

                cursor.execute(f"SELECT MAX(IND) FROM {table} WHERE UUID = ?", (uuid_val,))
                max_ind = cursor.fetchone()[0]
                next_ind = (max_ind + 1) if max_ind is not None else 0

                field_str = ", ".join(["UUID", "IND"] + field_list)
                sql = f"INSERT INTO {table} ({field_str}) VALUES ({', '.join(['?'] * (2 + len(field_list)))})"

                insert_count = 0
                for values in value_list:
                    row = [uuid_val, next_ind] + values
                    cursor.execute(sql, row)
                    next_ind += 1
                    insert_count += 1

                result["action"]["inserts"][table] = result["action"]["inserts"].get(table, 0) + insert_count

            # Insert into Registry
            cursor.execute("INSERT INTO Registry (UUID) VALUES (?);", (uuid_val,))
            existing_uuids.add(uuid_val)

        except Exception as e:
            result["errors"].append(f"group '{group_name}': {str(e)}")
            result["status"] = "partial"

    conn.commit()

    if result["errors"] and not result["action"]["inserts"]:
        result["status"] = "error"
    elif result["errors"]:
        result["status"] = "partial"

    return result
