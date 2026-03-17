import sys
import os
from werkzeug.security import generate_password_hash

sys.path.append(os.getcwd())
from app import create_app
from models import db
from models.user import User

app = create_app()
with app.app_context():
    admin = User.query.filter_by(email='admin@oliver-ugwi.com').first()
    if admin:
        admin.password_hash = generate_password_hash('admin123')
        db.session.commit()
        print("Admin password updated to 'admin123' successfully!")
    else:
        print("Admin not found!")
