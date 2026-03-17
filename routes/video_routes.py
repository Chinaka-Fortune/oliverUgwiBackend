import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.hero_video import HeroVideo
from models.user import User
from models import db
from werkzeug.utils import secure_filename

video_bp = Blueprint('videos', __name__)

ALLOWED_EXTENSIONS = {'mp4', 'webm', 'ogg'}

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
        filename = secure_filename(file.filename)
        unique_filename = f"hero_{uuid.uuid4().hex}_{filename}"
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
        
        file_url = f"/uploads/{unique_filename}"
        
        new_video = HeroVideo(
            filename=unique_filename,
            url=file_url
        )
        db.session.add(new_video)
        db.session.commit()
        
        return jsonify({"msg": "Video uploaded successfully", "video": new_video.to_dict()}), 201
    
    return jsonify({"msg": "File type not allowed. Please upload mp4, webm, or ogg."}), 400

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

    # Delete file from filesystem
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], video.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

    db.session.delete(video)
    db.session.commit()
    
    return jsonify({"msg": "Video deleted successfully"}), 200
