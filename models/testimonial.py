from . import db
from datetime import datetime

class Testimonial(db.Model):
    __tablename__ = 'testimonials'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(150), nullable=False)
    text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True) # Adding image URL support
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'text': self.text,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None
        }
