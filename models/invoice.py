from models import db
from datetime import datetime
import string
import random

def generate_invoice_id():
    """Generate a unique invoice ID like INV-2026-123456"""
    year = datetime.utcnow().year
    chars = string.digits
    while True:
        invoice_id = f"INV-{year}-{''.join(random.choice(chars) for _ in range(6))}"
        # Check if exists
        from models.invoice import Invoice
        if not Invoice.query.filter_by(invoice_id=invoice_id).first():
            return invoice_id

class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), nullable=True) # Optional
    
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    status = db.Column(db.String(50), default='Unpaid') # Paid, Unpaid, Overdue, Cancelled
    description = db.Column(db.String(255), nullable=True)
    
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('invoices', lazy=True))
    shipment = db.relationship('Shipment', backref=db.backref('invoices', lazy=True))

    def __init__(self, **kwargs):
        super(Invoice, self).__init__(**kwargs)
        if not self.invoice_id:
            self.invoice_id = generate_invoice_id()

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Unknown',
            'shipment_id': self.shipment_id,
            'tracking_id': self.shipment.tracking_id if self.shipment else None,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
