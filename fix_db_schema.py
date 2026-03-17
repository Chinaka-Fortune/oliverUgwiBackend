import sqlite3
import os

def check_and_add_columns():
    db_paths = [
        'oliverUgwiBackend/instance/oliver_ugwi.db',
        'oliverUgwiBackend/oliver_ugwi.db'
    ]
    
    for db_path in db_paths:
        if not os.path.exists(db_path):
            print(f"Skipping: Database not found at {db_path}")
            continue

        print(f"Processing database at {db_path}...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Columns to check/add for quote_requests table
        new_columns = [
            ('status', 'VARCHAR(50) DEFAULT "Pending"'),
            ('admin_reply', 'TEXT'),
            ('estimated_cost', 'VARCHAR(100)'),
            ('transit_time', 'VARCHAR(100)'),
            ('validity_period', 'VARCHAR(100)'),
            ('terms', 'TEXT'),
            ('updated_at', 'DATETIME')
        ]

        # Get existing columns
        cursor.execute("PRAGMA table_info(quote_requests)")
        existing_columns = [col[1] for col in cursor.fetchall()]

        for col_name, col_type in new_columns:
            if col_name not in existing_columns:
                print(f"Adding column {col_name} to quote_requests table...")
                try:
                    cursor.execute(f"ALTER TABLE quote_requests ADD COLUMN {col_name} {col_type}")
                except Exception as e:
                    print(f"Error adding {col_name}: {e}")
            else:
                print(f"Column {col_name} already exists.")

        conn.commit()
        conn.close()
    print("Database schema update complete.")

if __name__ == "__main__":
    check_and_add_columns()
