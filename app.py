import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from config import Config
from models import db
from routes.auth_routes import auth_bp
from routes.shipment_routes import shipment_bp
from routes.service_routes import service_bp
from routes.ticket_routes import ticket_bp
from routes.blog_routes import blog_bp
from routes.video_routes import video_bp
from routes.testimonial_routes import testimonial_bp
from routes.admin_routes import admin_bp
from routes.customer_routes import customer_bp
from routes.billing_routes import billing_bp
from models.contact import Contact
from flask_jwt_extended import JWTManager

load_dotenv()

from routes.communication_routes import comm_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.url_map.strict_slashes = False
    
    # Configure Upload Folder (Handle Vercel read-only filesystem)
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    try:
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        # Vercel functions are read-only except for /tmp.
        # We catch the error so the app can still boot. 
        # For production file uploads, an external service (like S3/Supabase Storage) is required.
        pass

    # CORS Configuration - Pull from ENV or use defaults
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5175").split(',')
    CORS(app, origins=allowed_origins, supports_credentials=True)
    db.init_app(app)
    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth', strict_slashes=False)
    app.register_blueprint(shipment_bp, url_prefix='/api/shipments', strict_slashes=False)
    app.register_blueprint(service_bp, url_prefix='/api/services', strict_slashes=False)
    app.register_blueprint(ticket_bp, url_prefix='/api/tickets', strict_slashes=False)
    app.register_blueprint(blog_bp, url_prefix='/api/blogs', strict_slashes=False)
    app.register_blueprint(comm_bp, url_prefix='/api/comm', strict_slashes=False)
    app.register_blueprint(video_bp, url_prefix='/api/videos', strict_slashes=False)
    app.register_blueprint(testimonial_bp, url_prefix='/api/testimonials', strict_slashes=False)
    app.register_blueprint(admin_bp, url_prefix='/api/admin', strict_slashes=False)
    app.register_blueprint(customer_bp, url_prefix='/api/customer', strict_slashes=False)
    app.register_blueprint(billing_bp, url_prefix='/api/billing', strict_slashes=False)

    @app.route('/')
    def index():
        return jsonify({
            "status": "online",
            "message": "Oliver Ugwi API is running."
        }), 200

    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "service": "OLIVER-UGWI API"})


    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Port 5000 is used locally. Vercel automatically assigns a port.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

