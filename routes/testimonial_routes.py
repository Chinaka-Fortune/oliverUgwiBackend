from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename
from models import db
from models.testimonial import Testimonial
from models.user import User
import cloudinary
import cloudinary.uploader

testimonial_bp = Blueprint('testimonial_routes', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@testimonial_bp.route('/', methods=['GET'])
def get_testimonials():
    try:
        testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
        return jsonify([t.to_dict() for t in testimonials]), 200
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500

@testimonial_bp.route('/', methods=['POST'])
@jwt_required()
def create_testimonial():
    from models.user import User
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"message": "Unauthorized"}), 403

    # Check for multipart/form-data (file upload) vs application/json
    if request.content_type.startswith('multipart/form-data'):
        data = request.form
        name = data.get('name')
        role = data.get('role')
        text = data.get('text')
    else:
        data = request.get_json()
        name = data.get('name') if data else None
        role = data.get('role') if data else None
        text = data.get('text') if data else None

    if not name or not role or not text:
        return jsonify({"message": "Name, role, and text are required"}), 400

    image_url = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '' and allowed_file(file.filename):
            try:
                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    file,
                    folder="testimonials"
                )
                image_url = upload_result.get("secure_url")
            except Exception as e:
                print(f"Cloudinary upload error: {e}")
                # Fallback or error handled below

    try:
        new_testimonial = Testimonial(
            name=name,
            role=role,
            text=text,
            image_url=image_url
        )
        db.session.add(new_testimonial)
        db.session.commit()
        return jsonify(new_testimonial.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error", "error": str(e)}), 500

@testimonial_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_testimonial(id):
    from models.user import User
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"message": "Unauthorized"}), 403

    testimonial = Testimonial.query.get_or_404(id)
    
    if request.content_type.startswith('multipart/form-data'):
        data = request.form
    else:
        data = request.get_json() or {}

    try:
        if 'name' in data and data['name']:
            testimonial.name = data['name']
        if 'role' in data and data['role']:
            testimonial.role = data['role']
        if 'text' in data and data['text']:
            testimonial.text = data['text']

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                try:
                    # Optional: Delete old image from Cloudinary if it was a Cloudinary URL
                    if testimonial.image_url and 'cloudinary' in testimonial.image_url:
                        try:
                            # Extract public_id from URL
                            public_id = testimonial.image_url.split('/')[-1].split('.')[0]
                            cloudinary.uploader.destroy(f"testimonials/{public_id}")
                        except:
                            pass

                    # Upload to Cloudinary
                    upload_result = cloudinary.uploader.upload(
                        file,
                        folder="testimonials"
                    )
                    testimonial.image_url = upload_result.get("secure_url")
                except Exception as e:
                    print(f"Cloudinary upload error: {e}")
        if 'name' in data:
            testimonial.name = data['name']
        if 'role' in data:
            testimonial.role = data['role']
        if 'text' in data:
            testimonial.text = data['text']

        db.session.commit()
        return jsonify(testimonial.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error", "error": str(e)}), 500

@testimonial_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_testimonial(id):
    from models.user import User
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"message": "Unauthorized"}), 403

    testimonial = Testimonial.query.get_or_404(id)

    try:
        # Delete associated image file from Cloudinary if it exists
        if testimonial.image_url and 'cloudinary' in testimonial.image_url:
            try:
                public_id = testimonial.image_url.split('/')[-1].split('.')[0]
                cloudinary.uploader.destroy(f"testimonials/{public_id}")
            except:
                pass
                
        db.session.delete(testimonial)
        db.session.commit()
        return jsonify({"message": "Testimonial deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error", "error": str(e)}), 500
