from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.ticket import Ticket
from models.user import User
from models import db
import string
import random

ticket_bp = Blueprint('tickets', __name__)

def generate_ticket_id():
    chars = string.digits
    return f"TKT-{837492 + random.randint(1, 10000)}"

@ticket_bp.route('/', methods=['GET'])
@jwt_required()
def get_tickets():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role == 'admin':
        tickets = Ticket.query.all()
    else:
        tickets = Ticket.query.filter_by(user_id=current_user_id).all()
        
    return jsonify({"tickets": [t.to_dict() for t in tickets]}), 200

@ticket_bp.route('/', methods=['POST'])
@jwt_required()
def create_ticket():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    new_ticket = Ticket(
        ticket_id=generate_ticket_id(),
        user_id=current_user_id,
        subject=data.get('subject'),
        status='Open',
        priority=data.get('priority', 'Medium')
    )
    
    db.session.add(new_ticket)
    db.session.commit()
    return jsonify({"msg": "Ticket created", "ticket": new_ticket.to_dict()}), 201

@ticket_bp.route('/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_ticket_status(id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Admin access required"}), 403
        
    ticket = Ticket.query.get(id)
    if not ticket:
        return jsonify({"msg": "Ticket not found"}), 404
        
    data = request.get_json()
    ticket.status = data.get('status', ticket.status)
    db.session.commit()
    return jsonify({"msg": "Ticket status updated", "ticket": ticket.to_dict()}), 200

@ticket_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_ticket(id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Admin access required"}), 403
        
    ticket = Ticket.query.get(id)
    if not ticket:
        return jsonify({"msg": "Ticket not found"}), 404
        
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"msg": "Ticket deleted successfully"}), 200
