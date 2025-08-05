def search_package(package: dict, conn, cursor, db_meta) -> dict:
    try:
        search = package
        table_results = []

        for table, fields in search.items():
            if table not in db_meta["tables"]:
                continue

            where_clauses = []
            parameters = []

            for field, logic in fields.items():
                if field not in db_meta["fields"][db_meta["tables"].index(table)]:
                    continue

                field_clauses = []

                # AND group
                and_group = logic.get("and", [])
                if and_group:
                    and_clauses = []
                    for rule in and_group:
                        if "equals" in rule:
                            and_clauses.append(f"{field} = ?")
                            parameters.append(rule["equals"])
                        elif "contains" in rule:
                            and_clauses.append(f"{field} LIKE ?")
                            parameters.append(f"%{rule['contains']}%")
                    if and_clauses:
                        field_clauses.append("(" + " AND ".join(and_clauses) + ")")

                # OR group
                or_group = logic.get("or", [])
                if or_group:
                    or_clauses = []
                    for rule in or_group:
                        if "equals" in rule:
                            or_clauses.append(f"{field} = ?")
                            parameters.append(rule["equals"])
                        elif "contains" in rule:
                            or_clauses.append(f"{field} LIKE ?")
                            parameters.append(f"%{rule['contains']}%")
                    if or_clauses:
                        field_clauses.append("(" + " OR ".join(or_clauses) + ")")

                if field_clauses:
                    where_clauses.append("(" + " OR ".join(field_clauses) + ")")

            if not where_clauses:
                continue

            sql = f"SELECT UUID FROM {table} WHERE " + " AND ".join(where_clauses)
            cursor.execute(sql, parameters)
            uuids = set(row[0] for row in cursor.fetchall())
            table_results.append(uuids)

        if not table_results:
            result = []
        else:
            matching_uuids = set.intersection(*table_results)
            result = list(matching_uuids)

        return {
            "action": "search",
            "status": "success",
            "result": result
        }

    except Exception as e:
        return {
            "action": "search",
            "status": "error",
            "result": [],
            "message": str(e)
        }
