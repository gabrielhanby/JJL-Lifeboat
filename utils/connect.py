import sqlite3
import json
import os
import sys

# Load DB config
SETTINGS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../settings/database.json"))

try:
    with open(SETTINGS_PATH, "r") as f:
        db_config = json.load(f)
except Exception as e:
    print(f"[ERROR] Failed to load database settings: {e}")
    sys.exit(1)

# Pick database (static for now)
DB_NAME = "database.db"

if DB_NAME not in db_config:
    print(f"[ERROR] '{DB_NAME}' not found in database.json.")
    sys.exit(1)

DB_PATH = db_config[DB_NAME]["path"]

# Connect to the database
try:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
except Exception as e:
    print(f"[ERROR] Failed to connect to database '{DB_NAME}': {e}")
    sys.exit(1)

# Validate schema and collect metadata
def validate_schema_and_extract_meta():
    meta = {
        "tables": [],
        "fields": []
    }

    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        if "Registry" not in tables:
            raise ValueError("Missing required 'Registry' table.")

        for table in tables:
            if table == "sqlite_sequence":
                continue

            cursor.execute(f"PRAGMA table_info({table});")
            cols = [row[1] for row in cursor.fetchall()]

            # Save metadata
            meta["tables"].append(table)
            meta["fields"].append(cols)

            if table == "Registry":
                if cols != ["UUID"]:
                    raise ValueError("'Registry' table must only contain 'UUID'")
            else:
                if "UUID" not in cols or "IND" not in cols:
                    raise ValueError(f"Table '{table}' missing required fields 'UUID' and/or 'IND'.")

        return meta

    except Exception as e:
        print(f"[ERROR] Schema validation failed: {e}")
        conn.close()
        sys.exit(1)

db_meta = validate_schema_and_extract_meta()

def close_connection():
    conn.close()
