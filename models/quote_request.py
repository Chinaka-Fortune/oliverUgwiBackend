from models import db
from datetime import datetime

class QuoteRequest(db.Model):
    __tablename__ = 'quote_requests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    instructions = db.Column(db.Text, nullable=True)
    file_url = db.Column(db.String(255), nullable=True) # Optional file attachment URL
    
    # Status for admin tracking: Pending, Replied, Ignored
    status = db.Column(db.String(50), default='Pending')
    admin_reply = db.Column(db.Text, nullable=True) # General comments
    
    # Structured reply fields
    estimated_cost = db.Column(db.String(100), nullable=True)
    transit_time = db.Column(db.String(100), nullable=True)
    validity_period = db.Column(db.String(100), nullable=True)
    terms = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'service': self.service,
            'origin': self.origin,
            'destination': self.destination,
            'weight': self.weight,
            'description': self.description,
            'instructions': self.instructions,
            'file_url': self.file_url,
            'status': self.status,
            'admin_reply': self.admin_reply,
            'estimated_cost': self.estimated_cost,
            'transit_time': self.transit_time,
            'validity_period': self.validity_period,
            'terms': self.terms,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
