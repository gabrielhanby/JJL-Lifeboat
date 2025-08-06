import sqlite3
import os

# Target path
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/docket.db"))

# Ensure parent directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Connect and create tables
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Drop all tables (for clean reset)
tables = [
    "Contacts", "Matters", "Addresses", "Phone_Numbers", "Email_Addresses",
    "Notes", "Tracking", "Registry"
]
for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table}")

# Create Registry (UUID only)
cursor.execute("""
CREATE TABLE Registry (
    UUID TEXT PRIMARY KEY
)
""")

# Create Contacts
cursor.execute("""
CREATE TABLE Contacts (
    UUID TEXT,
    IND INTEGER,
    entity TEXT,
    prefix TEXT,
    first_name TEXT,
    middle_name TEXT,
    last_name TEXT,
    suffix TEXT,
    full_name TEXT,
    gender TEXT,
    date_of_birth TEXT,
    location_of_birth TEXT,
    social_security_number TEXT,
    PRIMARY KEY (UUID, IND)
)
""")

# Create Matters
cursor.execute("""
CREATE TABLE Matters (
    UUID TEXT,
    IND INTEGER,
    group_name TEXT,
    status TEXT,
    sub_status TEXT,
    PRIMARY KEY (UUID, IND)
)
""")

# Create Addresses
cursor.execute("""
CREATE TABLE Addresses (
    UUID TEXT,
    IND INTEGER,
    street TEXT,
    city TEXT,
    county TEXT,
    state TEXT,
    zip_code TEXT,
    country TEXT,
    address_type TEXT,
    is_primary BOOLEAN,
    PRIMARY KEY (UUID, IND)
)
""")

# Create Phone Numbers
cursor.execute("""
CREATE TABLE Phone_Numbers (
    UUID TEXT,
    IND INTEGER,
    phone_number TEXT,
    phone_type TEXT,
    is_primary BOOLEAN,
    PRIMARY KEY (UUID, IND)
)
""")

# Create Email Addresses
cursor.execute("""
CREATE TABLE Email_Addresses (
    UUID TEXT,
    IND INTEGER,
    email_address TEXT,
    email_type TEXT,
    is_primary BOOLEAN,
    PRIMARY KEY (UUID, IND)
)
""")

# Create Notes
cursor.execute("""
CREATE TABLE Notes (
    UUID TEXT,
    IND INTEGER,
    subject TEXT,
    body TEXT,
    created TEXT,
    updated TEXT,
    PRIMARY KEY (UUID, IND)
)
""")

# Create Tracking
cursor.execute("""
CREATE TABLE Tracking (
    UUID TEXT,
    IND INTEGER,
    created TEXT,
    state_filed TEXT,
    entity_type TEXT,
    tags TEXT,
    PRIMARY KEY (UUID, IND)
)
""")

# Commit and close
conn.commit()
conn.close()

print(f"[SETUP] Created database at: {DB_PATH}")
