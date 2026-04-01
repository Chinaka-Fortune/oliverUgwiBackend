import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.hero_video import HeroVideo
from models.user import User
from models import db
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
import cloudinary.utils
import time

video_bp = Blueprint('videos', __name__)

ALLOWED_EXTENSIONS = {'mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@video_bp.route('/', methods=['GET'])
def get_videos():
    """Public: Get all hero videos"""
    videos = HeroVideo.query.order_by(HeroVideo.created_at.asc()).all()
    return jsonify({"videos": [v.to_dict() for v in videos]}), 200

@video_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_video():
    """Admin Only: Upload a hero video"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized. Admin access required."}), 403

    if 'file' not in request.files:
        return jsonify({"msg": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                file, 
                resource_type="video", 
                folder="hero_videos"
            )
            
            file_url = upload_result.get("secure_url")
            public_id = upload_result.get("public_id") # We'll save this in the filename column to easily delete later
            
            new_video = HeroVideo(
                filename=public_id,
                url=file_url
            )
            db.session.add(new_video)
            db.session.commit()
            
            return jsonify({"msg": "Video uploaded successfully", "video": new_video.to_dict()}), 201
        except Exception as e:
            return jsonify({"msg": f"Cloudinary upload failed: {str(e)}"}), 500
    
    return jsonify({"msg": f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

@video_bp.route('/signature', methods=['GET'])
@jwt_required()
def get_signature():
    """Admin Only: Generate a Cloudinary signature for direct frontend upload"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized. Admin access required."}), 403

    timestamp = int(time.time())
    params = {
        "timestamp": timestamp,
        "folder": "hero_videos"
    }
    
    # Get configuration from environment variable CLOUDINARY_URL or direct config
    config = cloudinary.config()
    signature = cloudinary.utils.api_sign_request(params, config.api_secret)
    
    return jsonify({
        "signature": signature,
        "timestamp": timestamp,
        "cloud_name": config.cloud_name,
        "api_key": config.api_key,
        "folder": "hero_videos"
    }), 200

@video_bp.route('/save', methods=['POST'])
@jwt_required()
def save_video_metadata():
    """Admin Only: Save the URL and Public ID of a video uploaded directly by the frontend"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized. Admin access required."}), 403

    data = request.json
    if not data or 'url' not in data or 'public_id' not in data:
        return jsonify({"msg": "Missing required data (url, public_id)"}), 400

    new_video = HeroVideo(
        filename=data['public_id'],
        url=data['url']
    )
    db.session.add(new_video)
    db.session.commit()
    
    return jsonify({"msg": "Video metadata saved successfully", "video": new_video.to_dict()}), 201

@video_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_video(id):
    """Admin Only: Delete a hero video"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized. Admin access required."}), 403

    video = HeroVideo.query.get(id)
    if not video:
        return jsonify({"msg": "Video not found"}), 404

    # Delete file from Cloudinary 
    try:
        # For Cloudinary, the filename column stores the public_id
        cloudinary.uploader.destroy(video.filename, resource_type="video")
    except Exception as e:
        print(f"Error deleting file from Cloudinary: {e}")

    db.session.delete(video)
    db.session.commit()
    
    return jsonify({"msg": "Video deleted successfully"}), 200
