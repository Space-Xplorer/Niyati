"""
Authentication module for Project Niyati (Flask version).

Provides:
  - get_secret_key()          — returns the JWT secret
  - token_required            — decorator: validates JWT, injects current_user
  - admin_required            — decorator: token_required + Admin role check
  - auth_bp                   — Flask Blueprint with /register and /login routes
"""

import os
import jwt
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, request, jsonify, current_app
from flask_bcrypt import Bcrypt

from database import db
from models import User

bcrypt = Bcrypt()

auth_bp = Blueprint('auth', __name__)


def get_secret_key() -> str:
    """Return the JWT secret key from environment (with dev fallback)."""
    return os.environ.get('JWT_SECRET', 'my-super-secret-niyati-key')


# ─────────────────────────────────────────────────────────────────────────────
# Decorators
# ─────────────────────────────────────────────────────────────────────────────

def token_required(f):
    """
    Decorator that validates the Bearer JWT in the Authorization header.
    Injects `current_user` (a User model instance) as the first argument.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Authorization header missing or malformed'}), 401

        token = auth_header.split(' ', 1)[1]
        try:
            payload = jwt.decode(token, get_secret_key(), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        user_id = payload.get('user_id')
        if user_id is None:
            return jsonify({'message': 'Invalid token: missing user_id'}), 401

        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return jsonify({'message': 'User not found'}), 401

        # Attach token claims so downstream code can read them if needed
        user.token_role = payload.get('role')
        user.token_gstin = payload.get('gstin')

        return f(user, *args, **kwargs)

    return decorated


def admin_required(f):
    """
    Decorator that combines token_required with an Admin role check.
    Injects `current_user` as the first argument.
    """
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'Admin':
            return jsonify({'message': 'Admin access required'}), 403
        return f(current_user, *args, **kwargs)

    return decorated


# ─────────────────────────────────────────────────────────────────────────────
# Auth routes  (mounted at /api/auth by the app)
# ─────────────────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['POST'])
def register():
    """POST /api/auth/register — create a new user account."""
    data = request.get_json(silent=True) or {}

    email = data.get('email', '').strip()
    password = data.get('password', '')
    role = data.get('role', '')
    gstin = data.get('gstin')

    if not email or not password or not role:
        return jsonify({'message': 'email, password and role are required'}), 400

    if role not in ('Admin', 'Business_Owner'):
        return jsonify({'message': 'Invalid role. Must be Admin or Business_Owner'}), 400

    if role == 'Business_Owner' and not gstin:
        return jsonify({'message': 'gstin is required for Business_Owner'}), 400

    # Only one admin allowed
    if role == 'Admin':
        if User.query.filter_by(role='Admin').count() > 0:
            return jsonify({'message': 'Admin registration is restricted. An admin already exists.'}), 403

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 409

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password_hash=password_hash, role=role, gstin=gstin)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error registering user: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """POST /api/auth/login — authenticate and return a JWT."""
    data = request.get_json(silent=True) or {}

    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'message': 'email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = jwt.encode(
        {
            'user_id': user.id,
            'role': user.role,
            'gstin': user.gstin,
            'exp': datetime.utcnow() + timedelta(hours=24),
        },
        get_secret_key(),
        algorithm='HS256',
    )

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'gstin': user.gstin,
        },
    })
