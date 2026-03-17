from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.invoice import Invoice
from models.user import User
from models.shipment import Shipment
from datetime import datetime

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_invoices():
    """Admin: Get all invoices"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized. Admin access required."}), 403
    
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    return jsonify({"invoices": [i.to_dict() for i in invoices]}), 200

@billing_bp.route('/my-invoices', methods=['GET'])
@jwt_required()
def get_my_invoices():
    """Customer: Get own invoices"""
    user_id = get_jwt_identity()
    invoices = Invoice.query.filter_by(user_id=user_id).order_by(Invoice.created_at.desc()).all()
    return jsonify({"invoices": [i.to_dict() for i in invoices]}), 200

@billing_bp.route('/', methods=['POST'])
@jwt_required()
def create_invoice():
    """Admin: Create new invoice"""
    user_id = get_jwt_identity()
    admin = User.query.get(user_id)
    
    if not admin or admin.role != 'admin':
        return jsonify({"msg": "Unauthorized. Admin access required."}), 403
    
    data = request.get_json()
    
    # Validation
    required_fields = ['user_id', 'amount', 'due_date']
    if not all(field in data for field in required_fields):
        return jsonify({"msg": "Missing required fields"}), 400
    
    try:
        new_invoice = Invoice(
            user_id=data['user_id'],
            shipment_id=data.get('shipment_id'),
            amount=float(data['amount']),
            currency=data.get('currency', 'USD'),
            status=data.get('status', 'Unpaid'),
            description=data.get('description'),
            due_date=datetime.fromisoformat(data['due_date'].replace('Z', '')) if data.get('due_date') else None
        )
        
        db.session.add(new_invoice)
        db.session.commit()
        
        return jsonify({"msg": "Invoice created successfully", "invoice": new_invoice.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error creating invoice: {str(e)}"}), 500

@billing_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_invoice_details(id):
    """Admin or Owner: Get invoice details"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    invoice = Invoice.query.get_or_404(id)
    
    if user.role != 'admin' and invoice.user_id != user_id:
        return jsonify({"msg": "Unauthorized."}), 403
    
    return jsonify({"invoice": invoice.to_dict()}), 200

@billing_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_invoice(id):
    """Admin: Update invoice"""
    user_id = get_jwt_identity()
    admin = User.query.get(user_id)
    
    if not admin or admin.role != 'admin':
        return jsonify({"msg": "Unauthorized. Admin access required."}), 403
    
    invoice = Invoice.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'amount' in data: invoice.amount = float(data['amount'])
        if 'status' in data: invoice.status = data['status']
        if 'description' in data: invoice.description = data['description']
        if 'due_date' in data: 
            invoice.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '')) if data['due_date'] else None
        if 'currency' in data: invoice.currency = data['currency']
        
        db.session.commit()
        return jsonify({"msg": "Invoice updated successfully", "invoice": invoice.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error updating invoice: {str(e)}"}), 500

@billing_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_invoice(id):
    """Admin: Delete invoice"""
    user_id = get_jwt_identity()
    admin = User.query.get(user_id)
    
    if not admin or admin.role != 'admin':
        return jsonify({"msg": "Unauthorized. Admin access required."}), 403
    
    invoice = Invoice.query.get_or_404(id)
    
    try:
        db.session.delete(invoice)
        db.session.commit()
        return jsonify({"msg": "Invoice deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error deleting invoice: {str(e)}"}), 500
