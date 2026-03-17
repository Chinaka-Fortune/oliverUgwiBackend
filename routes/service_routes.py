from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.service import Service
from models.user import User
from models import db

service_bp = Blueprint('services', __name__)

@service_bp.route('/', methods=['GET'])
def get_services():
    services = Service.query.all()
    return jsonify({"services": [s.to_dict() for s in services]}), 200

@service_bp.route('/', methods=['POST'])
@jwt_required()
def create_service():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Admin access required"}), 403
        
    data = request.get_json()
    new_service = Service(
        name=data.get('name'),
        type=data.get('type'),
        status=data.get('status', 'Active'),
        price_factor=data.get('price_factor')
    )
    db.session.add(new_service)
    db.session.commit()
    return jsonify({"msg": "Service created", "service": new_service.to_dict()}), 201

@service_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_service(service_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Admin access required"}), 403
        
    service = Service.query.get(service_id)
    if not service:
        return jsonify({"msg": "Service not found"}), 404
        
    data = request.get_json()
    service.name = data.get('name', service.name)
    service.type = data.get('type', service.type)
    service.status = data.get('status', service.status)
    service.price_factor = data.get('price_factor', service.price_factor)
    
    db.session.commit()
    return jsonify({"msg": "Service updated", "service": service.to_dict()}), 200

@service_bp.route('/<int:service_id>', methods=['DELETE'])
@jwt_required()
def delete_service(service_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Admin access required"}), 403
        
    service = Service.query.get(service_id)
    if not service:
        return jsonify({"msg": "Service not found"}), 404
        
    db.session.delete(service)
    db.session.commit()
    return jsonify({"msg": "Service deleted"}), 200
