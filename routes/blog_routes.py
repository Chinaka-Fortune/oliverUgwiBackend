import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.blog import Blog
from models.comment import Comment
from models.like import Like
from models.user import User
from models import db
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader

blog_bp = Blueprint('blogs', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@blog_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Admin Only: Upload an image file"""
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
        try:
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                file,
                folder="blog_images"
            )
            file_url = upload_result.get("secure_url")
            return jsonify({"msg": "File uploaded successfully", "url": file_url}), 201
        except Exception as e:
            return jsonify({"msg": f"Cloudinary upload failed: {str(e)}"}), 500
    
    return jsonify({"msg": "File type not allowed"}), 400

@blog_bp.route('/', methods=['GET'])
def get_blogs():
    """Public: Get all blog posts"""
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    return jsonify({"blogs": [b.to_dict() for b in blogs]}), 200

@blog_bp.route('/<int:id>', methods=['GET'])
@jwt_required(optional=True)
def get_blog(id):
    """Public: Get single blog post with comments and like status"""
    blog = Blog.query.get(id)
    if not blog:
        return jsonify({"msg": "Blog post not found"}), 404
    
    current_user_id = get_jwt_identity()
    user_liked = False
    if current_user_id:
        like = Like.query.filter_by(blog_id=id, user_id=current_user_id).first()
        user_liked = True if like else False

    # Get comments
    comments = [c.to_dict() for c in blog.comments]
    
    blog_data = blog.to_dict()
    blog_data['comments'] = comments
    blog_data['user_liked'] = user_liked
    
    return jsonify({"blog": blog_data}), 200

@blog_bp.route('/', methods=['POST'])
@jwt_required()
def create_blog():
    """Admin Only: Create a new blog post"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized. Admin access required."}), 403
        
    data = request.get_json()
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({"msg": "Title and content are required"}), 400
        
    # Defensive check for author name
    author_name = getattr(user, 'name', 'Admin') or 'Admin'
        
    new_blog = Blog(
        title=data.get('title'),
        content=data.get('content'),
        excerpt=data.get('excerpt', data.get('content')[:150] + '...'),
        category=data.get('category', 'Uncategorized'),
        author=author_name,
        image_url=data.get('image_url')
    )
    
    db.session.add(new_blog)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
    
    return jsonify({"msg": "Blog post created", "blog": new_blog.to_dict()}), 201

@blog_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_blog(id):
    """Admin Only: Update an existing blog post"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized. Admin access required."}), 403
        
    blog = Blog.query.get(id)
    if not blog:
        return jsonify({"msg": "Blog post not found"}), 404
        
    data = request.get_json()
    blog.title = data.get('title', blog.title)
    blog.content = data.get('content', blog.content)
    blog.excerpt = data.get('excerpt', blog.excerpt)
    blog.category = data.get('category', blog.category)
    blog.image_url = data.get('image_url', blog.image_url)
    
    db.session.commit()
    
    return jsonify({"msg": "Blog post updated", "blog": blog.to_dict()}), 200

@blog_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_blog(id):
    """Admin Only: Delete a blog post"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Unauthorized. Admin access required."}), 403
        
    blog = Blog.query.get(id)
    if not blog:
        return jsonify({"msg": "Blog post not found"}), 404
        
    # Delete from Cloudinary if applicable
    if blog.image_url and 'cloudinary' in blog.image_url:
        try:
            public_id = blog.image_url.split('/')[-1].split('.')[0]
            cloudinary.uploader.destroy(f"blog_images/{public_id}")
        except:
            pass

    db.session.delete(blog)
    db.session.commit()
    
    return jsonify({"msg": "Blog post deleted successfully"}), 200

@blog_bp.route('/<int:id>/like', methods=['POST'])
@jwt_required()
def toggle_like(id):
    """Auth User: Toggle like on a blog post"""
    current_user_id = get_jwt_identity()
    blog = Blog.query.get(id)
    if not blog:
        return jsonify({"msg": "Blog post not found"}), 404
        
    existing_like = Like.query.filter_by(blog_id=id, user_id=current_user_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({"msg": "Unliked", "liked": False, "count": len(blog.likes)}), 200
    else:
        new_like = Like(blog_id=id, user_id=current_user_id)
        db.session.add(new_like)
        db.session.commit()
        return jsonify({"msg": "Liked", "liked": True, "count": len(blog.likes)}), 201

@blog_bp.route('/<int:id>/comments', methods=['POST'])
@jwt_required()
def add_comment(id):
    """Auth User: Add a comment to a blog post"""
    current_user_id = get_jwt_identity()
    blog = Blog.query.get(id)
    if not blog:
        return jsonify({"msg": "Blog post not found"}), 404
        
    data = request.get_json()
    if not data or not data.get('content'):
        return jsonify({"msg": "Comment content is required"}), 400
        
    new_comment = Comment(
        blog_id=id,
        user_id=current_user_id,
        content=data.get('content')
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify({"msg": "Comment added", "comment": new_comment.to_dict()}), 201

@blog_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """Comment Owner or Admin: Delete a comment"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    comment = Comment.query.get(comment_id)
    
    if not comment:
        return jsonify({"msg": "Comment not found"}), 404
        
    if comment.user_id != current_user_id and user.role != 'admin':
        return jsonify({"msg": "Unauthorized to delete this comment"}), 403
        
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({"msg": "Comment deleted"}), 200

@blog_bp.route('/seed', methods=['POST'])
def seed_blogs():
    """One-time route to seed mock data, clears existing blogs first for a clean restore"""
    # Clear existing to ensure "original contents" are restored as requested
    Blog.query.delete()
    Like.query.delete()
    Comment.query.delete()
    
    posts = [
        {
            "title": "The Future of African Maritime Logistics in 2024",
            "content": "Exploring the technological advancements and infrastructural investments shaping the future of maritime trade across the African continent. Africa is poised for a logistics revolution as ports modernize and digital tracking becomes the norm.",
            "excerpt": "Exploring the technological advancements and infrastructural investments shaping the future of maritime trade across the African continent.",
            "category": "Logistics Trends",
            "author": "Admin"
        },
        {
            "title": "Navigating New Customs Regulations for FMCG Exports",
            "content": "A comprehensive guide to understanding and complying with the latest customs regulations for Fast-Moving Consumer Goods. Keeping up with regulatory changes is crucial for maintaining a seamless supply chain.",
            "excerpt": "A comprehensive guide to understanding and complying with the latest customs regulations for Fast-Moving Consumer Goods.",
            "category": "Customs & Compliance",
            "author": "OLIVER UGWI"
        },
        {
            "title": "Green Shipping: Reducing Carbon Footprint in Supply Chains",
            "content": "How forward-thinking logistics companies are adopting sustainable practices to minimize environmental impact. From eco-friendly packaging to optimized routing, the industry is going green.",
            "excerpt": "How forward-thinking logistics companies are adopting sustainable practices to minimize environmental impact.",
            "category": "Sustainability",
            "author": "Admin"
        },
        {
            "title": "Air Cargo Demands Peak: What You Need to Know",
            "content": "Analyzing the sudden surge in air cargo demand and strategies to secure space during peak seasons. As global trade routes shift, air freight remains a critical component of time-sensitive logistics.",
            "excerpt": "Analyzing the sudden surge in air cargo demand and strategies to secure space during peak seasons.",
            "category": "Logistics Trends",
            "author": "Admin"
        },
        {
            "title": "Strategic Product Sourcing in Southeast Asia",
            "content": "Key considerations and risk management strategies for B2B distributors sourcing merchandise from Asian markets. Understanding local manufacturing landscapes and quality control is key to successful sourcing.",
            "excerpt": "Key considerations and risk management strategies for B2B distributors sourcing merchandise from Asian markets.",
            "category": "Global Trade",
            "author": "OLIVER UGWI"
        },
        {
            "title": "The Importance of Real-Time Tracking Technology",
            "content": "Why visibility is the new currency in modern logistics operations and how technology is delivering transparency. Customers now expect minute-by-minute updates on their shipments.",
            "excerpt": "Why visibility is the new currency in modern logistics operations and how technology is delivering transparency.",
            "category": "Logistics Trends",
            "author": "Admin"
        }
    ]
    
    for p in posts:
        blog = Blog(
            title=p['title'],
            content=p['content'],
            excerpt=p['excerpt'],
            category=p['category'],
            author=p['author']
        )
        db.session.add(blog)
    
    db.session.commit()
    return jsonify({"msg": "Success! Blogs restored for testing."}), 201
