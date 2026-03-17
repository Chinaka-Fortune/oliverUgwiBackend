from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
from models import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({"msg": "Missing required fields (name, email, password)"}), 400
        
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"msg": "Email already exists"}), 409

    hashed_password = generate_password_hash(data.get('password'))
    new_user = User(
        name=data.get('name'),
        email=data.get('email'),
        password_hash=hashed_password,
        role=data.get('role', 'customer')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"msg": "User created successfully", "user": new_user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Missing required fields (email, password)"}), 400

    user = User.query.filter_by(email=data.get('email')).first()
    
    if not user or not check_password_hash(user.password_hash, data.get('password')):
        return jsonify({"msg": "Invalid email or password"}), 401
        
    if not user.is_active:
        return jsonify({"msg": "Account is inactive"}), 403

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "msg": "Login successful", 
        "access_token": access_token, 
        "user": user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    return jsonify(user.to_dict()), 200

@auth_bp.route('/update-password', methods=['PUT'])
@jwt_required()
def update_password():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({"msg": "Missing current or new password"}), 400
        
    if not check_password_hash(user.password_hash, current_password):
        return jsonify({"msg": "Incorrect current password"}), 401
        
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    return jsonify({"msg": "Password updated successfully"}), 200

@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    data = request.get_json()
    user.name = data.get('name', user.name)
    user.phone = data.get('phone', user.phone)
    user.address = data.get('address', user.address)
    
    db.session.commit()
    
    return jsonify({"msg": "Profile updated successfully", "user": user.to_dict()}), 200
