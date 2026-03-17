import sys
import os

sys.path.append(os.getcwd())

from app import create_app
from models import db
from models.user import User
from werkzeug.security import generate_password_hash

def reset_customer():
    app = create_app()
    with app.app_context():
        customer = User.query.filter_by(email='customer_user@oliverugwi.com').first()
        if customer:
            customer.password_hash = generate_password_hash('customer-pass-2026')
            customer.name = 'Customer User'
            customer.role = 'customer'
            customer.is_active = True
            db.session.commit()
            print(f"Password reset successfully for: {customer.email}")
            print(f"  Name: {customer.name}")
            print(f"  Role: {customer.role}")
            print(f"  Active: {customer.is_active}")
        else:
            # Create if doesn't exist
            new_customer = User(
                name='Customer User',
                email='customer_user@oliverugwi.com',
                password_hash=generate_password_hash('customer-pass-2026'),
                role='customer'
            )
            db.session.add(new_customer)
            db.session.commit()
            print("Customer user created successfully!")

if __name__ == '__main__':
    reset_customer()
