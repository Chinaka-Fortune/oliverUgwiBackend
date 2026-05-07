from models import db
from datetime import datetime
import string
import random
from models.user import User

def generate_tracking_id():
    """Generate a unique tracking ID like OUGSL-123456"""
    chars = string.digits
    while True:
        tracking_id = f"OUGSL-{''.join(random.choice(chars) for _ in range(6))}"
        # Check if exists
        from models.shipment import Shipment
        if not Shipment.query.filter_by(tracking_id=tracking_id).first():
            return tracking_id

class Shipment(db.Model):
    __tablename__ = 'shipments'

    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Optional, can belong to a user
    
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    current_location = db.Column(db.String(100), nullable=True)
    
    status = db.Column(db.String(50), default='Pending') # Pending, In Transit, Arrived POD, Cleared, Delivered
    type = db.Column(db.String(50), nullable=False) # Maritime, Air Cargo, etc.
    estimated_deliveryDate = db.Column('estimated_delivery_date', db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    revenue = db.Column(db.Float, default=0.0)

    # New Tracking Fields
    bl_awb_no = db.Column(db.String(100), nullable=True)
    consignment = db.Column(db.String(200), nullable=True)
    vessel_airline = db.Column(db.String(100), nullable=True)
    pol = db.Column(db.String(100), nullable=True)
    ets = db.Column(db.String(100), nullable=True)
    pod = db.Column(db.String(100), nullable=True)
    eta = db.Column(db.String(100), nullable=True)
    
    user = db.relationship('User', backref=db.backref('shipments', lazy=True))

    def __init__(self, **kwargs):
        super(Shipment, self).__init__(**kwargs)
        if not self.tracking_id:
            self.tracking_id = generate_tracking_id()
        if not self.current_location:
            self.current_location = self.origin

    def to_dict(self):
        return {
            'id': self.id,
            'tracking_id': self.tracking_id,
            'user_id': self.user_id,
            'origin': self.origin,
            'destination': self.destination,
            'current_location': self.current_location,
            'status': self.status,
            'type': self.type,
            'estimated_deliveryDate': self.estimated_deliveryDate.isoformat() if self.estimated_deliveryDate else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'revenue': self.revenue,
            'bl_awb_no': self.bl_awb_no,
            'consignment': self.consignment,
            'vessel_airline': self.vessel_airline,
            'pol': self.pol,
            'ets': self.ets,
            'pod': self.pod,
            'eta': self.eta
        }
