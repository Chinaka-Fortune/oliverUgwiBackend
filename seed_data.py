import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from app import create_app
from models import db
from models.blog import Blog
from models.testimonial import Testimonial
from models.like import Like
from models.comment import Comment
from models.user import User
from models.shipment import Shipment
from models.ticket import Ticket
from models.invoice import Invoice
from werkzeug.security import generate_password_hash

def seed_data():
    app = create_app()
    with app.app_context():
        print("Cleaning up existing data...")
        # Clear existing data
        Blog.query.delete()
        Testimonial.query.delete()
        Like.query.delete()
        Comment.query.delete()
        Ticket.query.delete()
        Shipment.query.delete()
        User.query.filter(User.role != 'admin').delete()
        db.session.commit()

        print("Seeding original blog posts...")
        blog_posts = [
            {
                "title": "The Future of African Maritime Logistics in 2024",
                "content": "Exploring the technological advancements and infrastructural investments shaping the future of maritime trade across the African continent. Africa is poised for a logistics revolution as ports modernize and digital tracking becomes the norm.",
                "excerpt": "Exploring the technological advancements and infrastructural investments shaping the future of maritime trade across the African continent.",
                "category": "Logistics Trends",
                "author": "Admin"
            },
            {
                "title": "Navigating New Customs Regulations for FMCG Exports",
                "content": "A comprehensive guide to understanding and complying with the latest customs regulations for Fast-Moving Consumer Goods. Keeping up with regulatory changes is crucial for maintaining a seamless supply chain.",
                "excerpt": "A comprehensive guide to understanding and complying with the latest customs regulations for Fast-Moving Consumer Goods.",
                "category": "Customs & Compliance",
                "author": "OLIVER UGWI"
            },
            {
                "title": "Green Shipping: Reducing Carbon Footprint in Supply Chains",
                "content": "How forward-thinking logistics companies are adopting sustainable practices to minimize environmental impact. From eco-friendly packaging to optimized routing, the industry is going green.",
                "excerpt": "How forward-thinking logistics companies are adopting sustainable practices to minimize environmental impact.",
                "category": "Sustainability",
                "author": "Admin"
            },
            {
                "title": "Air Cargo Demands Peak: What You Need to Know",
                "content": "Analyzing the sudden surge in air cargo demand and strategies to secure space during peak seasons. As global trade routes shift, air freight remains a critical component of time-sensitive logistics.",
                "excerpt": "Analyzing the sudden surge in air cargo demand and strategies to secure space during peak seasons.",
                "category": "Logistics Trends",
                "author": "Admin"
            },
            {
                "title": "Strategic Product Sourcing in Southeast Asia",
                "content": "Key considerations and risk management strategies for B2B distributors sourcing merchandise from Asian markets. Understanding local manufacturing landscapes and quality control is key to successful sourcing.",
                "excerpt": "Key considerations and risk management strategies for B2B distributors sourcing merchandise from Asian markets.",
                "category": "Global Trade",
                "author": "OLIVER UGWI"
            },
            {
                "title": "The Importance of Real-Time Tracking Technology",
                "content": "Why visibility is the new currency in modern logistics operations and how technology is delivering transparency. Customers now expect minute-by-minute updates on their shipments.",
                "excerpt": "Why visibility is the new currency in modern logistics operations and how technology is delivering transparency.",
                "category": "Logistics Trends",
                "author": "Admin"
            }
        ]

        for p in blog_posts:
            blog = Blog(
                title=p['title'],
                content=p['content'],
                excerpt=p['excerpt'],
                category=p['category'],
                author=p['author']
            )
            db.session.add(blog)

        print("Seeding original testimonials...")
        testimonials = [
            {
                "name": "Chizoba Ezirim",
                "role": "Senior Partner, LENab Consulting",
                "text": "Working with OLIVER-UGWI GLOBAL SERVICES LTD has been an absolute pleasure. Their team of skilled professionals is not only knowledgeable in their field but also dedicated to providing top-notch service and support. They took the time to understand our unique needs and developed a tailored solution that exceeded our expectations. I cannot recommend OLIVER-UGWI GLOBAL SERVICES LTD highly enough for any business seeking innovative maritime solutions and exceptional customer care."
            },
            {
                "name": "Daniel Ogwara",
                "role": "MD/CEO, Ogwara Haulage Services",
                "text": "Every time We have used OLIVER-UGWI GLOBAL SERVICES LTD, We have been pleased with their service delivery. The professionalism and efficiency with which they render their services are satisfactory and We highly recommend them. Their dedication to ensuring our cargo moves smoothly through the complex logistics process is truly commendable."
            },
            {
                "name": "Angela Ibeneme",
                "role": "MD, M & D Delite Foods",
                "text": "OLIVER-UGWI GLOBAL SERVICES LTD has been our go-to choice for maritime and air cargo logistics, and they've never disappointed. Their team go above and beyond to ensure our consignments are handled with care and precision. Their competitive rates and swift response to our requirements have saved us both time and money. It's a pleasure working with a company that values customer satisfaction as much as they do."
            },
            {
                "name": "Godwin Aigbadon",
                "role": "CEO, Sagacity Global Projects",
                "text": "OLIVER-UGWI GLOBAL SERVICES LTD has consistently been our trusted partner for clearing and forwarding services. Their reliability and attention to detail have made our import operations significantly smoother. They have a deep understanding of the maritime industry, and their solutions are always tailored to our specific needs. We appreciate their commitment to excellence."
            },
            {
                "name": "Amechi Afam",
                "role": "CEO, God's Grace Enterprise",
                "text": "In the international trade industry, OLIVER-UGWI GLOBAL SERVICES LTD stands out as a beacon of professionalism and reliability. Their team's dedication to customer satisfaction is evident in every interaction. We have experienced reduced delays and improved efficiency in our operations since partnering with them. Their integrated logistics approach has truly made a difference."
            }
        ]

        for t in testimonials:
            testi = Testimonial(
                name=t['name'],
                role=t['role'],
                text=t['text']
            )
            db.session.add(testi)

        print("Seeding sample users...")
        # Seed Customer
        customer_user = User.query.filter_by(email="customer_user@oliverugwi.com").first()
        if not customer_user:
            customer_user = User(
                name="Sample Customer",
                email="customer_user@oliverugwi.com",
                password_hash=generate_password_hash("customer-pass-2026"),
                role="customer"
            )
            db.session.add(customer_user)
        
        # Seed Admin
        admin_user = User.query.filter_by(email="admin@oliver-ugwi.com").first()
        if not admin_user:
            admin_user = User(
                name="Admin User",
                email="admin@oliver-ugwi.com",
                password_hash=generate_password_hash("admin123"),
                role="admin"
            )
            db.session.add(admin_user)
            
        db.session.commit()

        print("Seeding sample shipments...")
        shipments = [
            {
                "origin": "Lagos, Nigeria",
                "destination": "London, UK",
                "type": "Maritime",
                "status": "In Transit",
                "revenue": 1500.0,
                "user_id": customer_user.id
            },
            {
                "origin": "New York, USA",
                "destination": "Lagos, Nigeria",
                "type": "Air Cargo",
                "status": "Pending",
                "revenue": 2400.0,
                "user_id": customer_user.id
            },
            {
                "origin": "Shanghai, China",
                "destination": "Abuja, Nigeria",
                "type": "Maritime",
                "status": "Delivered",
                "revenue": 3200.0,
                "user_id": customer_user.id
            }
        ]

        for s_data in shipments:
            s = Shipment(**s_data)
            db.session.add(s)

        print("Seeding sample tickets...")
        tickets = [
            {
                "ticket_id": "TKT-1001",
                "subject": "Delayed shipment inquiry",
                "status": "Open",
                "priority": "High",
                "user_id": customer_user.id
            },
            {
                "ticket_id": "TKT-1002",
                "subject": "Billing issue",
                "status": "Open",
                "priority": "Medium",
                "user_id": customer_user.id
            }
        ]

        for t_data in tickets:
            t = Ticket(**t_data)
            db.session.add(t)

        print("Seeding sample invoices...")
        invoices = [
            {
                "user_id": customer_user.id,
                "amount": 1500.0,
                "currency": "USD",
                "status": "Pending",
                "description": "Shipping fees for maritime cargo (Lagos -> London)",
                "due_date": date(2026, 4, 15)
            },
            {
                "user_id": customer_user.id,
                "amount": 2400.0,
                "currency": "USD",
                "status": "Paid",
                "description": "Air freight handling for electronics shipment",
                "due_date": date(2026, 3, 20)
            }
        ]

        for i_data in invoices:
            inv = Invoice(**i_data)
            db.session.add(inv)

        db.session.commit()
        print("Data seeded successfully!")

if __name__ == '__main__':
    seed_data()
