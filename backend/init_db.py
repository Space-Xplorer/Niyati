"""
Database Initialization Script

This script creates all database tables for Project Niyati.
Run this before starting the application for the first time.

Usage:
    python init_db.py
"""

import os
from dotenv import load_dotenv
from flask import Flask
from database import db
from models import (
    User, RawInvoice, RawEwayBill, EntityMaster,
    EngineeredFeatures, RiskPrediction, FraudPattern,
    AuditNarrative, ShapePlot
)

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///niyati.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

def init_database():
    """Create all database tables"""
    with app.app_context():
        print("Creating database tables...")
        
        # Drop all tables (use with caution in production!)
        # db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("✓ Database tables created successfully!")
        print("\nCreated tables:")
        print("  - users")
        print("  - raw_invoices")
        print("  - raw_eway_bills")
        print("  - entity_master")
        print("  - engineered_features")
        print("  - risk_predictions")
        print("  - fraud_patterns")
        print("  - audit_narratives")
        print("  - shape_plots")
        
        # Verify tables
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\nVerified {len(tables)} tables in database")

if __name__ == "__main__":
    init_database()
