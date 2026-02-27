"""
Create test users with proper roles
"""
from database import db
from models import User
from flask import Flask
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///niyati.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
bcrypt = Bcrypt(app)

def create_test_users():
    with app.app_context():
        print("Creating test users...")
        # Continue inserting test users; existing ones will be skipped automatically at the insert phase
        # Create test users
        test_users = [
            {
                'email': 'admin@gstn.gov.in',
                'password': 'admin123',
                'role': 'Admin',
                'gstin': 'ADMIN_NODE'
            },
            {
                'email': 'business1@example.com',
                'password': 'business123',
                'role': 'Business_Owner',
                'gstin': '29AABCT1332L1Z5'
            },
            {
                'email': 'business2@example.com',
                'password': 'business123',
                'role': 'Business_Owner',
                'gstin': '27AABCU9603R1ZM'
            },
            {
                'email': 'taxpayer@example.com',
                'password': 'taxpayer123',
                'role': 'Business_Owner',
                'gstin': '07AABCU9603R1ZX'
            }
        ]
        
        for user_data in test_users:
            # Check if user already exists
            existing = User.query.filter_by(email=user_data['email']).first()
            if existing:
                print(f"  User {user_data['email']} already exists, skipping...")
                continue
            
            # Create new user
            hashed_password = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
            new_user = User(
                email=user_data['email'],
                password_hash=hashed_password,
                role=user_data['role'],
                gstin=user_data['gstin']
            )
            db.session.add(new_user)
            print(f"  ✓ Created {user_data['role']}: {user_data['email']} (GSTIN: {user_data['gstin']})")
        
        db.session.commit()
        
        # Display all users
        print("\nAll users in database:")
        all_users = User.query.all()
        for u in all_users:
            print(f"  - {u.email} | Role: {u.role} | GSTIN: {u.gstin or 'N/A'}")
        
        print("\n✅ Test users created successfully!")
        print("\nTest Credentials:")
        print("  Admin: admin@gstn.gov.in / admin123")
        print("  Business 1: business1@example.com / business123 (GSTIN: 29AABCT1332L1Z5)")
        print("  Business 2: business2@example.com / business123 (GSTIN: 27AABCU9603R1ZM)")
        print("  Taxpayer: taxpayer@example.com / taxpayer123 (GSTIN: 07AABCU9603R1ZX)")

if __name__ == '__main__':
    create_test_users()
