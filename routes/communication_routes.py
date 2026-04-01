from flask import Blueprint, request, jsonify
from models import db
from models.quote_request import QuoteRequest
import os
import uuid
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User

# Since service_routes.py exists and is small, we can add them there or create a new one.
# Let's create a specific communication_bp for these interactions.

from models.contact import Contact
from utils.email import send_email


comm_bp = Blueprint('communication', __name__)

@comm_bp.route('/contact', methods=['POST'])
def handle_contact():
    data = request.json
    try:
        new_contact = Contact(
            firstName=data.get('firstName'),
            lastName=data.get('lastName'),
            email=data.get('email'),
            phone=data.get('phone'),
            service=data.get('service'),
            message=data.get('message')
        )
        db.session.add(new_contact)
        db.session.commit()

        # Automated Email Notifications
        admin_email = os.environ.get('MAIL_DEFAULT_SENDER', 'info@oliverugwi.com')
        
        # 1. Notify Admin
        admin_subject = f"New Contact Inquiry: {new_contact.firstName} {new_contact.lastName}"
        admin_body = f"""
        <h3>New Inquiry Received</h3>
        <p><strong>Name:</strong> {new_contact.firstName} {new_contact.lastName}</p>
        <p><strong>Email:</strong> {new_contact.email}</p>
        <p><strong>Phone:</strong> {new_contact.phone}</p>
        <p><strong>Service:</strong> {new_contact.service}</p>
        <p><strong>Message:</strong></p>
        <p>{new_contact.message}</p>
        """
        send_email(admin_email, admin_subject, admin_body, is_html=True)

        # 2. Acknowledge Customer
        customer_subject = "Thank you for contacting OLIVER-UGWI"
        customer_body = f"""
        <h3>Hello {new_contact.firstName},</h3>
        <p>Thank you for reaching out to OLIVER-UGWI GLOBAL SERVICES LTD. We have received your inquiry regarding <strong>{new_contact.service}</strong>.</p>
        <p>Our team will review your message and get back to you shortly.</p>
        <br>
        <p>Best regards,</p>
        <p><strong>OLIVER-UGWI Team</strong></p>
        """
        send_email(new_contact.email, customer_subject, customer_body, is_html=True)

        return jsonify({"message": "Inquiry received successfully", "contact": new_contact.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error saving contact inquiry", "error": str(e)}), 500

@comm_bp.route('/admin/contacts', methods=['GET'])
@jwt_required()
def get_contacts():
    """Admin Only: Get all contact inquiries"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403

    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    return jsonify([c.to_dict() for c in contacts]), 200

@comm_bp.route('/admin/contacts/<int:id>', methods=['PUT'])
@jwt_required()
def update_contact(id):
    """Admin Only: Update contact status or notes"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403

    contact = Contact.query.get_or_404(id)
    data = request.get_json()
    
    try:
        contact.status = data.get('status', contact.status)
        contact.notes = data.get('notes', contact.notes)
        db.session.commit()
        return jsonify({"message": "Contact updated successfully", "contact": contact.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating contact", "error": str(e)}), 500

@comm_bp.route('/admin/contacts/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_contact(id):
    """Admin Only: Delete a contact inquiry"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403

    contact = Contact.query.get_or_404(id)
    try:
        db.session.delete(contact)
        db.session.commit()
        return jsonify({"message": "Contact inquiry deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error deleting contact", "error": str(e)}), 500

@comm_bp.route('/admin/contacts/send-email', methods=['POST'])
@jwt_required()
def send_contact_email():
    """Admin Only: Send email directly to contact from dashboard"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.get_json()
    to_emails = data.get('to_emails') # Can be string or list
    subject = data.get('subject')
    body = data.get('body')

    if not to_emails or not subject or not body:
        return jsonify({"msg": "Missing required email fields"}), 400

    # Handle comma-separated list of emails from bulk action
    recipients = to_emails.split(',') if isinstance(to_emails, str) else to_emails
    success_count = 0
    
    for email in recipients:
        email = email.strip()
        if email:
            if send_email(email, subject, body):
                success_count += 1
                
    if success_count > 0:
        return jsonify({"message": f"Successfully sent {success_count} email(s)"}), 200
    else:
        return jsonify({"message": "Failed to send emails. Check configuration."}), 500


@comm_bp.route('/quotes', methods=['POST'])
def handle_quote_request():
    # Handle multipart/form-data for file upload
    if request.content_type.startswith('multipart/form-data'):
        data = request.form
    else:
        # Fallback for simple JSON if no file is sent
        data = request.get_json() or {}

    name = data.get('name')
    email = data.get('email')
    service = data.get('service')
    origin = data.get('origin', '')
    destination = data.get('destination', '')
    weight = data.get('weight')
    description = data.get('description', '')
    instructions = data.get('instructions', '')
    # Optionally associate with a user if logged in
    user_id = None
    from flask_jwt_extended import decode_token
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        try:
            token = auth_header.split(' ')[1]
            decoded = decode_token(token)
            user_id = decoded['sub']
        except:
            pass

    if not name or not email or not service:
        return jsonify({"message": "Name, email, and service are required"}), 400

    file_url = None
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '':
            from flask import current_app
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            filename = secure_filename(file.filename)
            unique_filename = f"quote_{uuid.uuid4().hex[:8]}_{filename}"
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            file_url = f"/uploads/{unique_filename}"

    try:
        new_quote = QuoteRequest(
            name=name,
            email=email,
            service=service,
            origin=origin,
            destination=destination,
            weight=float(weight) if weight and str(weight).strip() else None,
            description=description,
            instructions=instructions,
            file_url=file_url
        )
        # If we had a user_id field in QuoteRequest, we would set it here.
        # However, checking the model, there isn't one. We will rely on email matching for now.
        
        db.session.add(new_quote)
        db.session.commit()

        # Automated Email Notifications
        admin_email = os.environ.get('MAIL_DEFAULT_SENDER', 'info@oliverugwi.com')
        
        # 1. Notify Admin
        admin_subject = f"New Quote Request: {new_quote.name}"
        admin_body = f"""
        <h3>New Quote Request Received</h3>
        <p><strong>Name:</strong> {new_quote.name}</p>
        <p><strong>Email:</strong> {new_quote.email}</p>
        <p><strong>Service:</strong> {new_quote.service}</p>
        <p><strong>Origin:</strong> {new_quote.origin}</p>
        <p><strong>Destination:</strong> {new_quote.destination}</p>
        <p><strong>Description:</strong> {new_quote.description}</p>
        """
        send_email(admin_email, admin_subject, admin_body, is_html=True)

        # 2. Acknowledge Customer
        customer_subject = "Quote Request Received - OLIVER-UGWI"
        customer_body = f"""
        <h3>Hello {new_quote.name},</h3>
        <p>We have received your request for a quote regarding <strong>{new_quote.service}</strong> from {new_quote.origin} to {new_quote.destination}.</p>
        <p>Our team is currently calculating the estimates and will provide you with a detailed quote shortly.</p>
        <br>
        <p>Best regards,</p>
        <p><strong>OLIVER-UGWI Team</strong></p>
        """
        send_email(new_quote.email, customer_subject, customer_body, is_html=True)

        return jsonify({"message": "Quote request submitted successfully", "quote": new_quote.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Quote Save Error: {str(e)}")
        return jsonify({"message": "Error saving quote request", "error": str(e)}), 500

@comm_bp.route('/quotes', methods=['GET'])
@jwt_required()
def get_quote_requests():
    """Admin Only: Get all quote requests"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403

    quotes = QuoteRequest.query.order_by(QuoteRequest.created_at.desc()).all()
    return jsonify([q.to_dict() for q in quotes]), 200

@comm_bp.route('/quotes/<int:id>/reply', methods=['POST'])
@jwt_required()
def reply_to_quote(id):
    """Admin Only: Reply to a quote request with structured data"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403

    quote = QuoteRequest.query.get_or_404(id)
    data = request.get_json()
    
    try:
        quote.admin_reply = data.get('reply') # General comments
        quote.estimated_cost = data.get('estimated_cost')
        quote.transit_time = data.get('transit_time')
        quote.validity_period = data.get('validity_period')
        quote.terms = data.get('terms')
        quote.status = 'Replied'
        
        db.session.commit()
        return jsonify({"message": "Reply saved successfully", "quote": quote.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error saving reply", "error": str(e)}), 500

@comm_bp.route('/quotes/<int:id>/reply', methods=['DELETE'])
@jwt_required()
def delete_quote_reply(id):
    """Admin Only: Delete/Clear a reply for a quote request"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403

    quote = QuoteRequest.query.get_or_404(id)
    
    try:
        quote.admin_reply = None
        quote.estimated_cost = None
        quote.transit_time = None
        quote.validity_period = None
        quote.terms = None
        quote.status = 'Pending'
        
        db.session.commit()
        return jsonify({"message": "Reply deleted successfully", "quote": quote.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error deleting reply", "error": str(e)}), 500

@comm_bp.route('/quotes/<int:id>', methods=['PUT'])
@jwt_required()
def update_quote_request(id):
    """Admin Only: Update a quote request details"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403

    quote = QuoteRequest.query.get_or_404(id)
    data = request.get_json()
    
    try:
        # Update allowed fields
        quote.origin = data.get('origin', quote.origin)
        quote.destination = data.get('destination', quote.destination)
        if 'weight' in data:
            quote.weight = float(data['weight']) if data['weight'] else None
        quote.description = data.get('description', quote.description)
        quote.instructions = data.get('instructions', quote.instructions)
        quote.status = data.get('status', quote.status)
        
        db.session.commit()
        return jsonify({"message": "Quote updated successfully", "quote": quote.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating quote", "error": str(e)}), 500

@comm_bp.route('/quotes/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_quote_request(id):
    """Admin Only: Delete a quote request"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403

    quote = QuoteRequest.query.get_or_404(id)
    
    try:
        db.session.delete(quote)
        db.session.commit()
        return jsonify({"message": "Quote request deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error deleting quote request", "error": str(e)}), 500

@comm_bp.route('/my-quotes', methods=['GET'])
@jwt_required()
def get_my_quotes():
    """Customer: Get their own quote requests based on email"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Fetch quotes matching the user's email
    quotes = QuoteRequest.query.filter_by(email=user.email).order_by(QuoteRequest.created_at.desc()).all()
    return jsonify([q.to_dict() for q in quotes]), 200
