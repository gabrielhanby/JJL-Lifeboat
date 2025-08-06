def handle(package: dict, conn, cursor, db_meta) -> dict:
    result = {
        "status": "success",
        "errors": [],
        "action": {
            "matches": []
        }
    }

    try:
        search = package
        table_results = []

        for table, fields in search.items():
            if table not in db_meta["tables"]:
                result["errors"].append(f"Table '{table}' does not exist.")
                continue

            where_clauses = []
            parameters = []

            for field, logic in fields.items():
                if field not in db_meta["fields"][db_meta["tables"].index(table)]:
                    result["errors"].append(f"Field '{field}' does not exist in table '{table}'.")
                    continue

                and_group = logic.get("and", [])
                or_group = logic.get("or", [])

                and_clauses = []
                or_clauses = []

                for rule in and_group:
                    if "equals" in rule:
                        and_clauses.append(f"{field} = ?")
                        parameters.append(rule["equals"])
                    elif "contains" in rule:
                        and_clauses.append(f"{field} LIKE ?")
                        parameters.append(f"%{rule['contains']}%")

                for rule in or_group:
                    if "equals" in rule:
                        or_clauses.append(f"{field} = ?")
                        parameters.append(rule["equals"])
                    elif "contains" in rule:
                        or_clauses.append(f"{field} LIKE ?")
                        parameters.append(f"%{rule['contains']}%")

                field_condition_parts = []

                if and_clauses:
                    field_condition_parts.append("(" + " AND ".join(and_clauses) + ")")
                if or_clauses:
                    field_condition_parts.append("(" + " OR ".join(or_clauses) + ")")

                if field_condition_parts:
                    where_clauses.append("(" + " OR ".join(field_condition_parts) + ")")

            if not where_clauses:
                continue

            sql = f"SELECT UUID FROM {table} WHERE " + " AND ".join(where_clauses)
            cursor.execute(sql, parameters)
            rows = cursor.fetchall()
            uuids = set(row[0] for row in rows)
            table_results.append(uuids)

        if len(table_results) == 1:
            result["action"]["matches"] = list(table_results[0])
        elif table_results:
            result["action"]["matches"] = list(set.intersection(*table_results))
        else:
            result["action"]["matches"] = []

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
        result["action"]["matches"] = []

    return result
