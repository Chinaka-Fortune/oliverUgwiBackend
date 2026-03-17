from app import create_app
from models import db
from models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    
    # Check if admin already exists
    admin = User.query.filter_by(email="admin@oliver-ugwi.com").first()
    if not admin:
        admin = User(
            name="Admin User",
            email="admin@oliver-ugwi.com",
            password_hash=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin)
        print("Admin user created.")
    else:
        print("Admin user already exists.")
        
    # Check if customer already exists
    customer = User.query.filter_by(email="customer_user@oliverugwi.com").first()
    if not customer:
        customer = User(
            name="Customer User",
            email="customer_user@oliverugwi.com",
            password_hash=generate_password_hash("customer-pass-2026"),
            role="customer"
        )
        db.session.add(customer)
        print("Customer user created.")
    else:
        print("Customer user already exists.")
        
    db.session.commit()
    print("Database seeded successfully.")
