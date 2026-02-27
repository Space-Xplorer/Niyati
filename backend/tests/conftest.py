"""
Pytest Configuration and Fixtures

This module provides shared fixtures for all tests in the Project Niyati test suite.
"""

import pytest
import os
import sys
from flask import Flask

# Add backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import db
from models import User


@pytest.fixture(scope='session')
def flask_app():
    """
    Create a Flask application for testing.
    
    This fixture creates a test database and provides a Flask app context
    for all tests.
    """
    app = Flask(__name__)
    
    # Configure test database (in-memory SQLite)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        yield app
        
        # Cleanup
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def db_session(flask_app):
    """
    Provide a database session for each test function.
    
    This fixture ensures each test starts with a clean database state.
    """
    with flask_app.app_context():
        # Begin a transaction
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Bind session to connection
        session = db.create_scoped_session(
            options={"bind": connection, "binds": {}}
        )
        db.session = session
        
        yield session
        
        # Rollback transaction
        transaction.rollback()
        connection.close()
        session.remove()


@pytest.fixture
def client(flask_app):
    """
    Provide a test client for making HTTP requests.
    """
    return flask_app.test_client()


@pytest.fixture
def auth_headers(flask_app):
    """
    Provide authentication headers for API requests.
    
    Creates a test user and returns JWT token in headers.
    """
    from flask_bcrypt import Bcrypt
    import jwt
    from datetime import datetime, timedelta
    
    bcrypt = Bcrypt()
    
    with flask_app.app_context():
        # Create test user
        test_user = User(
            email='test@example.com',
            password_hash=bcrypt.generate_password_hash('test123').decode('utf-8'),
            role='Admin',
            gstin=None
        )
        db.session.add(test_user)
        db.session.commit()
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': test_user.id,
            'role': test_user.role,
            'gstin': test_user.gstin,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, flask_app.config['SECRET_KEY'], algorithm="HS256")
        
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }


@pytest.fixture(autouse=True)
def reset_database(flask_app):
    """
    Automatically reset database before each test.
    """
    with flask_app.app_context():
        # Clear all tables
        db.session.query(User).delete()
        db.session.commit()
        
        yield
        
        # Cleanup after test
        db.session.rollback()
