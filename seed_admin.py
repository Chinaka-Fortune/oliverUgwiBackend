import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from app import create_app
from models import db
from models.user import User
from werkzeug.security import generate_password_hash

def seed_admin():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@oliver-ugwi.com').first()
        if not admin:
            admin = User(
                name='Super Admin',
                email='admin@oliver-ugwi.com',
                password_hash=generate_password_hash('adminpassword123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    seed_admin()
