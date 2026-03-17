import os
import sys
from werkzeug.security import generate_password_hash

# Add backend to path to import models
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_path)

from app import create_app
from models import db
from models.user import User

def update_admin():
    app = create_app()
    with app.app_context():
        # Find existing admin or any admin
        admin = User.query.filter_by(role='admin').first()
        
        new_email = 'admin@oliverugwi.com'
        new_password = 'ManifestationO2026#'
        
        if admin:
            print(f"Updating existing admin: {admin.email}")
            admin.email = new_email
            admin.password_hash = generate_password_hash(new_password)
            admin.name = 'Admin'
        else:
            print("No admin found, creating new one...")
            admin = User(
                name='Admin',
                email=new_email,
                password_hash=generate_password_hash(new_password),
                role='admin'
            )
            db.session.add(admin)
        
        db.session.commit()
        print(f"Admin credentials updated to: {new_email} / {new_password}")

if __name__ == '__main__':
    update_admin()
