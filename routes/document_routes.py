import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.document import Document
from models.user import User
from models import db
import cloudinary
import cloudinary.uploader

document_bp = Blueprint('documents', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@document_bp.route('/', methods=['GET'])
@jwt_required()
def get_documents():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    if user.role == 'admin':
        # Admin sees all documents
        documents = Document.query.order_by(Document.created_at.desc()).all()
    else:
        # Customers see only their own documents
        documents = Document.query.filter_by(user_id=current_user_id).order_by(Document.created_at.desc()).all()
        
    return jsonify({"documents": [d.to_dict() for d in documents]}), 200

@document_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    current_user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({"msg": "No file part"}), 400
        
    file = request.files['file']
    title = request.form.get('title', 'Untitled Document')
    
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        try:
            # Read file size manually by seeking to end then back to 0
            file.seek(0, os.SEEK_END)
            size_bytes = file.tell()
            file.seek(0, os.SEEK_SET)
            
            # Format size to human readable
            import math
            def format_sz(sz):
                if sz == 0: return "0 KB"
                i = int(math.floor(math.log(sz, 1024)))
                p = math.pow(1024, i)
                return f"{round(sz/p, 1)} {('B','KB','MB','GB')[i]}"
            
            formatted_size = format_sz(size_bytes)
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            
            # Use 'auto' to automatically handle raw files (docs) vs images (jpg)
            upload_result = cloudinary.uploader.upload(
                file, 
                resource_type="auto", 
                folder="documents"
            )
            
            new_doc = Document(
                title=title,
                file_url=upload_result.get("secure_url"),
                public_id=upload_result.get("public_id"),
                file_type=file_extension.upper(),
                size=formatted_size,
                user_id=current_user_id
            )
            
            db.session.add(new_doc)
            db.session.commit()
            
            return jsonify({"msg": "Document uploaded successfully", "document": new_doc.to_dict()}), 201
            
        except Exception as e:
            return jsonify({"msg": f"Cloudinary upload failed: {str(e)}"}), 500
            
    return jsonify({"msg": f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

@document_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_document(id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    doc = Document.query.get(id)
    if not doc:
        return jsonify({"msg": "Document not found"}), 404
        
    # Only Admin or the owner can update the title
    if user.role != 'admin' and str(doc.user_id) != str(current_user_id):
        return jsonify({"msg": "Unauthorized"}), 403
        
    data = request.get_json()
    if 'title' in data:
        doc.title = data['title']
        db.session.commit()
        return jsonify({"msg": "Document updated", "document": doc.to_dict()}), 200
        
    return jsonify({"msg": "No updates provided"}), 400

@document_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_document(id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    doc = Document.query.get(id)
    if not doc:
        return jsonify({"msg": "Document not found"}), 404
        
    # Only Admin or the owner can delete
    if user.role != 'admin' and str(doc.user_id) != str(current_user_id):
        return jsonify({"msg": "Unauthorized"}), 403
        
    try:
        if doc.public_id:
            try:
                cloudinary.uploader.destroy(doc.public_id, resource_type="raw")
            except:
                try:
                    cloudinary.uploader.destroy(doc.public_id, resource_type="image")
                except Exception as e:
                    print(f"Cloudinary destroy exception: {e}")
                
    except Exception as e:
        print(f"Error deleting file from Cloudinary: {e}")

    db.session.delete(doc)
    db.session.commit()
    
    return jsonify({"msg": "Document deleted successfully"}), 200
