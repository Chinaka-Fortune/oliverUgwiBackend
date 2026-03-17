import sqlite3
import os

def check_and_add_user_columns():
    db_paths = [
        'oliverUgwiBackend/instance/oliver_ugwi.db',
        'oliverUgwiBackend/oliver_ugwi.db'
    ]
    
    for db_path in db_paths:
        if not os.path.exists(db_path):
            continue

        print(f"Processing database at {db_path}...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Columns to check/add for users table
        new_columns = [
            ('phone', 'VARCHAR(20)'),
            ('address', 'VARCHAR(255)')
        ]

        # Get existing columns
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [col[1] for col in cursor.fetchall()]

        for col_name, col_type in new_columns:
            if col_name not in existing_columns:
                print(f"Adding column {col_name} to users table...")
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                except Exception as e:
                    print(f"Error adding {col_name}: {e}")
            else:
                print(f"Column {col_name} already exists.")

        conn.commit()
        conn.close()
    print("User schema update complete.")

if __name__ == "__main__":
    check_and_add_user_columns()
