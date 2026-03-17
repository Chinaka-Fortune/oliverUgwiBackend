from models import db
from datetime import datetime

class HeroVideo(db.Model):
    __tablename__ = 'hero_videos'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "url": self.url,
            "created_at": self.created_at.isoformat()
        }
