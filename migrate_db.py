import sqlite3
import os

db_path = r"c:\Users\CHINAKA FORTUNE C\Desktop\oliverUgwiApp\oliverUgwiBackend\instance\oliver_ugwi.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

try:
    print("Checking if revenue column exists...")
    cursor.execute("PRAGMA table_info(shipments)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'revenue' not in columns:
        print("Adding revenue column to shipments table...")
        cursor.execute("ALTER TABLE shipments ADD COLUMN revenue FLOAT DEFAULT 0.0")
        connection.commit()
        print("Revenue column added successfully.")
    else:
        print("Revenue column already exists.")
except Exception as e:
    print(f"Error: {e}")
finally:
    connection.close()
