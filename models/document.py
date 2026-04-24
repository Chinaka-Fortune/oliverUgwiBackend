from models import db
from datetime import datetime

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(255), nullable=True) # Cloudinary public ID for deletion
    file_type = db.Column(db.String(50), nullable=True)
    size = db.Column(db.String(50), nullable=True)
    
    # Who uploaded it or who it belongs to
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = db.relationship('User', backref=db.backref('documents', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'file_url': self.file_url,
            'public_id': self.public_id,
            'file_type': self.file_type,
            'size': self.size,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'user_name': self.user.name if self.user else 'Unknown',
            'user_email': self.user.email if self.user else 'Unknown'
        }
