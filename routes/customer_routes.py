from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.shipment import Shipment
from models.ticket import Ticket
from models.user import User
from models import db

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_customer_stats():
    """Get summarized statistics for the customer dashboard"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    try:
        # Active Shipments (status != 'Delivered')
        active_count = Shipment.query.filter_by(user_id=current_user_id).filter(Shipment.status != 'Delivered').count()
        
        # Completed Shipments (status == 'Delivered')
        completed_count = Shipment.query.filter_by(user_id=current_user_id).filter_by(status='Delivered').count()
        
        # Pending Actions (Open Tickets)
        open_tickets = Ticket.query.filter_by(user_id=current_user_id, status='Open').count()
        
        # Recent Shipments (last 3)
        recent_shipments = Shipment.query.filter_by(user_id=current_user_id).order_by(Shipment.created_at.desc()).limit(3).all()
        
        return jsonify({
            "stats": {
                "activeShipments": active_count,
                "completedShipments": completed_count,
                "pendingActions": open_tickets,
                "newDocuments": 2 # Mocked for now, or could count uploaded files if we had a model
            },
            "recentShipments": [s.to_dict() for s in recent_shipments]
        }), 200
        
    except Exception as e:
        return jsonify({"msg": f"Internal Server Error: {str(e)}"}), 500
