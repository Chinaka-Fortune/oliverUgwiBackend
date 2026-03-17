import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-key-oliver-ugwi')
    
    # Supabase/PostgreSQL compatibility fix for SQLAlchemy
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url or 'sqlite:///oliver_ugwi.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'super-jwt-secret-key')
