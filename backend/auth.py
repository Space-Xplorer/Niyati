import os
from functools import wraps
from flask import request, jsonify, Blueprint
import jwt
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from database import db
from models import User

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

def get_secret_key():
    return os.environ.get('JWT_SECRET_KEY', 'my-super-secret-niyati-key')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if auth header is present
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode token
            data = jwt.decode(token, get_secret_key(), algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
            if not current_user:
                return jsonify({'message': 'Invalid token (user not found)!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401

        # Pass current_user to the wrapped function
        return f(current_user, *args, **kwargs)

    return decorated

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'message': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Missing email or password'}), 400
    
    email = data['email']
    password = data['password']

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists. Please log in.'}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    role = data.get('role', 'user')
    new_user = User(email=email, password_hash=hashed_password, role=role)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error saving user: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Missing email or password'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Invalid credentials!'}), 401

    # Generate JWT
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=24) # Token expires in 24 hours
    }, get_secret_key(), algorithm="HS256")

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {'id': user.id, 'email': user.email, 'role': user.role}
    }), 200
