from models import db
from datetime import datetime

class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False) # 'Core', 'Service'
    status = db.Column(db.String(50), default='Active') # 'Active', 'Inactive', 'Maintenance'
    price_factor = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'status': self.status,
            'price_factor': self.price_factor,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
