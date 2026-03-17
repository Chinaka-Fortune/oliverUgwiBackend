import sys
import os
from werkzeug.security import generate_password_hash

sys.path.append(os.getcwd())
from app import create_app
from models import db
from models.user import User

app = create_app()
with app.app_context():
    # Helper to create or update user
    def update_user(email, name, password, role):
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"Updating existing user: {email}")
            user.password_hash = generate_password_hash(password)
            user.role = role
            user.name = name
        else:
            print(f"Creating new user: {email}")
            user = User(
                email=email,
                name=name,
                password_hash=generate_password_hash(password),
                role=role
            )
            db.session.add(user)
        db.session.commit()

    # Admin from access.txt
    update_user('admin@oliver-ugwi.com', 'Super Admin', 'admin123', 'admin')
    
    # Customer from access.txt
    update_user('customer_user@oliverugwi.com', 'Test Customer', 'customer-pass-2026', 'customer')

    print("\nDatabase sync complete.")

# Delete empty/confusion DB
confusion_db = 'instance/oliverugwi.db'
if os.path.exists(confusion_db):
    os.remove(confusion_db)
    print(f"Removed confusion database: {confusion_db}")
