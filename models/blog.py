from models import db
from datetime import datetime

class Blog(db.Model):
    __tablename__ = 'blogs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), default='Admin')
    image_url = db.Column(db.String(500), nullable=True) # For external or local storage paths
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    comments = db.relationship('Comment', backref='blog', lazy=True, cascade="all, delete-orphan")
    likes = db.relationship('Like', backref='blog', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'excerpt': self.excerpt,
            'category': self.category,
            'author': self.author,
            'image_url': self.image_url,
            'likes_count': len(self.likes),
            'comments_count': len(self.comments),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
