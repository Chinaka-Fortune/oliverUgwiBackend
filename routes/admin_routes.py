from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.shipment import Shipment
from models.user import User
from models.ticket import Ticket
from models import db
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get statistics for the admin dashboard"""
    current_user_id = get_jwt_identity()
    print(f"DEBUG: Dashboard stats request from user ID: {current_user_id}")
    user = User.query.get(current_user_id)
    
    if not user:
        print("DEBUG: User not found in database")
        return jsonify({"msg": "User not found"}), 404

    if user.role != 'admin':
        print(f"DEBUG: User {user.email} is not an admin (role: {user.role})")
        return jsonify({"msg": "Unauthorized. Admin access required."}), 403
        
    print("DEBUG: User is admin, proceeding to fetch stats")
        
    try:
        # 1. Total Active Shipments (status != 'Delivered')
        active_shipments_count = Shipment.query.filter(Shipment.status != 'Delivered').count()
        
        # 2. Total Users
        total_users_count = User.query.count()
        
        # 3. Open Support Tickets
        open_tickets_count = Ticket.query.filter_by(status='Open').count()
        
        # 4. Monthly Revenue
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        
        revenue_query = db.session.query(func.sum(Shipment.revenue)).filter(
            Shipment.created_at >= start_of_month
        ).scalar()
        monthly_revenue = float(revenue_query) if revenue_query is not None else 0.0
        
        # 5. Recent Shipments Activity (last 5)
        recent_shipments = Shipment.query.order_by(Shipment.created_at.desc()).limit(5).all()
        
        print(f"DEBUG: Successfully fetched stats. Revenue: {monthly_revenue}")
        
        return jsonify({
            "stats": {
                "activeShipments": active_shipments_count,
                "totalUsers": total_users_count,
                "openTickets": open_tickets_count,
                "monthlyRevenue": monthly_revenue
            },
            "recentActivity": [s.to_dict() for s in recent_shipments]
        }), 200
    except Exception as e:
        print(f"ERROR in get_dashboard_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"msg": f"Internal Server Error: {str(e)}"}), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Admin: Get all users for selection in invoices/management"""
    current_user_id = get_jwt_identity()
    admin = User.query.get(current_user_id)
    
    if not admin or admin.role != 'admin':
        return jsonify({"msg": "Unauthorized. Admin access required."}), 403
        
    users = User.query.all()
    return jsonify({"users": [u.to_dict() for u in users]}), 200
