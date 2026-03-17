from models import db
from datetime import datetime

class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Composite unique constraint to prevent duplicate likes
    __table_args__ = (db.UniqueConstraint('blog_id', 'user_id', name='_blog_user_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'blog_id': self.blog_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }
