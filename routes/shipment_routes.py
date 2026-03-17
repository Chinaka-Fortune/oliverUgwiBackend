from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.shipment import Shipment
from models.user import User
from models import db

shipment_bp = Blueprint('shipments', __name__)

@shipment_bp.route('/track/<tracking_id>', methods=['GET'])
def track_shipment(tracking_id):
    """Public route to track a shipment"""
    shipment = Shipment.query.filter_by(tracking_id=tracking_id).first()
    
    if not shipment:
        return jsonify({"msg": "Shipment not found"}), 404
        
    return jsonify({"shipment": shipment.to_dict()}), 200

@shipment_bp.route('/', methods=['POST'])
@jwt_required()
def create_shipment():
    """Admin only route to create shipments"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized. Admin access required."}), 403
        
    data = request.get_json()
    
    if not data or not data.get('origin') or not data.get('destination') or not data.get('type'):
        return jsonify({"msg": "Missing required fields"}), 400
        
    new_shipment = Shipment(
        user_id=data.get('user_id'), # Assign to specific customer if provided
        origin=data.get('origin'),
        destination=data.get('destination'),
        current_location=data.get('current_location', data.get('origin')),
        type=data.get('type'),
        status=data.get('status', 'Pending'),
        revenue=data.get('revenue', 0.0)
    )
    
    db.session.add(new_shipment)
    db.session.commit()
    
    return jsonify({"msg": "Shipment created successfully", "shipment": new_shipment.to_dict()}), 201

@shipment_bp.route('/my-shipments', methods=['GET'])
@jwt_required()
def get_my_shipments():
    """Get shipments for logged-in user"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role == 'admin':
        # Admin sees all shipments
        shipments = Shipment.query.all()
    else:
        # Customer sees their own
        shipments = Shipment.query.filter_by(user_id=current_user_id).all()
        
    return jsonify({"shipments": [s.to_dict() for s in shipments]}), 200

@shipment_bp.route('/<int:shipment_id>', methods=['DELETE'])
@jwt_required()
def delete_shipment(shipment_id):
    """Admin only route to delete shipment"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized. Admin access required."}), 403
        
    shipment = Shipment.query.get(shipment_id)
    if not shipment:
        return jsonify({"msg": "Shipment not found"}), 404
        
    db.session.delete(shipment)
    db.session.commit()
    
    return jsonify({"msg": "Shipment deleted successfully"}), 200
