import sqlite3
import os

# Target path
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/database.db"))

# Ensure parent directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Connect and create tables
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Drop if already exists (for testing reset)
cursor.execute("DROP TABLE IF EXISTS Contacts")
cursor.execute("DROP TABLE IF EXISTS Notes")
cursor.execute("DROP TABLE IF EXISTS Registry")

# Create Registry (UUID only)
cursor.execute("""
CREATE TABLE Registry (
    UUID TEXT PRIMARY KEY
)
""")

# Create Contacts table
cursor.execute("""
CREATE TABLE Contacts (
    UUID TEXT,
    IND INTEGER,
    first_name TEXT,
    middle_name TEXT,
    last_name TEXT,
    PRIMARY KEY (UUID, IND)
)
""")

# Create Notes table
cursor.execute("""
CREATE TABLE Notes (
    UUID TEXT,
    IND INTEGER,
    subject TEXT,
    body TEXT,
    PRIMARY KEY (UUID, IND)
)
""")

conn.commit()
conn.close()

print(f"[SETUP] Created database at: {DB_PATH}")
