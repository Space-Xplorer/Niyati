"""
Integration tests for authentication and RBAC functionality.
Tests user registration, login, JWT token generation, and RBAC filtering.
"""

import pytest
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import db
from models import User
import json


@pytest.fixture
def client():
    """Create a test client with in-memory database"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


def test_user_registration_with_admin_role(client):
    """Test user registration with Admin role"""
    response = client.post('/api/auth/register', 
        json={
            'email': 'admin@test.com',
            'password': 'admin123',
            'role': 'Admin'
        },
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'User registered successfully!'


def test_user_registration_with_business_owner_role(client):
    """Test user registration with Business_Owner role and GSTIN"""
    response = client.post('/api/auth/register',
        json={
            'email': 'owner@test.com',
            'password': 'owner123',
            'role': 'Business_Owner',
            'gstin': '27AAPFU0939F1ZV'
        },
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'User registered successfully!'


def test_user_registration_with_invalid_role(client):
    """Test user registration with invalid role should fail"""
    response = client.post('/api/auth/register',
        json={
            'email': 'invalid@test.com',
            'password': 'test123',
            'role': 'InvalidRole'
        },
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Invalid role' in data['message']


def test_user_login_returns_jwt_with_claims(client):
    """Test login returns JWT token with role and gstin claims"""
    # First register a user
    client.post('/api/auth/register',
        json={
            'email': 'test@test.com',
            'password': 'test123',
            'role': 'Business_Owner',
            'gstin': '27AAPFU0939F1ZV'
        },
        content_type='application/json'
    )
    
    # Then login
    response = client.post('/api/auth/login',
        json={
            'email': 'test@test.com',
            'password': 'test123'
        },
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data
    assert 'user' in data
    assert data['user']['role'] == 'Business_Owner'
    assert data['user']['gstin'] == '27AAPFU0939F1ZV'


def test_login_with_invalid_credentials(client):
    """Test login with invalid credentials should fail"""
    response = client.post('/api/auth/login',
        json={
            'email': 'nonexistent@test.com',
            'password': 'wrongpassword'
        },
        content_type='application/json'
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'Invalid credentials' in data['message']


def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token should fail"""
    response = client.get('/api/admin/data')
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'Token is missing' in data['message']


def test_admin_endpoint_with_admin_token(client):
    """Test admin endpoint access with Admin role token"""
    # Register admin user
    client.post('/api/auth/register',
        json={
            'email': 'admin@test.com',
            'password': 'admin123',
            'role': 'Admin'
        },
        content_type='application/json'
    )
    
    # Login to get token
    login_response = client.post('/api/auth/login',
        json={
            'email': 'admin@test.com',
            'password': 'admin123'
        },
        content_type='application/json'
    )
    
    token = json.loads(login_response.data)['token']
    
    # Access admin endpoint
    response = client.get('/api/admin/data',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'admin_email' in data


def test_admin_endpoint_with_business_owner_token(client):
    """Test admin endpoint access with Business_Owner role should fail"""
    # Register business owner
    client.post('/api/auth/register',
        json={
            'email': 'owner@test.com',
            'password': 'owner123',
            'role': 'Business_Owner',
            'gstin': '27AAPFU0939F1ZV'
        },
        content_type='application/json'
    )
    
    # Login to get token
    login_response = client.post('/api/auth/login',
        json={
            'email': 'owner@test.com',
            'password': 'owner123'
        },
        content_type='application/json'
    )
    
    token = json.loads(login_response.data)['token']
    
    # Try to access admin endpoint
    response = client.get('/api/admin/data',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'Admin access required' in data['message']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
