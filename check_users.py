import sqlite3
import os

def check_db(db_path):
    print(f"\nChecking {db_path}...")
    if not os.path.exists(db_path):
        print("File does not exist.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Tables: {tables}")
        
        for table in ['user', 'users']:
            if table in tables:
                print(f"Listing from table '{table}':")
                cursor.execute(f"SELECT id, email, role FROM {table}")
                users = cursor.fetchall()
                for user in users:
                    print(user)
        conn.close()
    except Exception as e:
        print(f"Error checking {db_path}: {e}")

check_db('instance/oliver_ugwi.db')
check_db('instance/oliverugwi.db')
