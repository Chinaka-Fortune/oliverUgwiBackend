import sqlite3
import os

def update_db():
    db_path = 'c:/Users/CHINAKA FORTUNE C/Desktop/oliverUgwiApp/oliverUgwiBackend/instance/oliver_ugwi.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    columns_to_add = [
        ('bl_awb_no', 'VARCHAR(100)'),
        ('consignment', 'VARCHAR(200)'),
        ('vessel_airline', 'VARCHAR(100)'),
        ('pol', 'VARCHAR(100)'),
        ('ets', 'VARCHAR(100)'),
        ('pod', 'VARCHAR(100)'),
        ('eta', 'VARCHAR(100)')
    ]

    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE shipments ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name}")
        except sqlite3.OperationalError as e:
            print(f"Column {col_name} might already exist or error: {e}")

    conn.commit()
    conn.close()
    print("Database update complete.")

if __name__ == '__main__':
    update_db()
