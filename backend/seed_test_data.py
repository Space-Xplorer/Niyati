#!/usr/bin/env python3
"""
Seed test data for Project Niyati

This script creates sample data for testing the dashboard without uploading CSV files.
"""

from app import app
from database import db
from models import (
    EntityMaster, RiskPrediction, FraudPattern, 
    AuditNarrative, EngineeredFeatures
)
from datetime import datetime

def seed_data():
    """Create sample test data"""
    with app.app_context():
        print("Seeding test data...")
        
        # Clear existing data
        print("Clearing existing test data...")
        RiskPrediction.query.delete()
        FraudPattern.query.delete()
        AuditNarrative.query.delete()
        EngineeredFeatures.query.delete()
        EntityMaster.query.delete()
        
        # Create sample entities
        print("Creating sample entities...")
        entities = [
            EntityMaster(
                gstin='29AABCT1332L1Z5',
                business_name='Tech Solutions Pvt Ltd',
                phone='9876543210',
                email='contact@techsolutions.com',
                address='123 Tech Park, Bangalore'
            ),
            EntityMaster(
                gstin='27AABCU9603R1ZM',
                business_name='Global Traders Inc',
                phone='9876543211',
                email='info@globaltraders.com',
                address='456 Trade Center, Mumbai'
            ),
            EntityMaster(
                gstin='07AABCU9603R1ZX',
                business_name='Retail Mart Ltd',
                phone='9876543212',
                email='support@retailmart.com',
                address='789 Market Street, Delhi'
            ),
        ]
        
        for entity in entities:
            db.session.add(entity)
        
        # Create sample risk predictions
        print("Creating sample risk predictions...")
        predictions = [
            RiskPrediction(
                gstin='29AABCT1332L1Z5',
                risk_probability=0.7850,
                risk_level='HIGH_RISK',
                top_driver_1='payment_gap_pct',
                top_driver_1_contribution=0.2500,
                top_driver_2='ghost_invoice_pct',
                top_driver_2_contribution=0.1800,
                top_driver_3='circular_trade_involvement',
                top_driver_3_contribution=0.1500,
                model_version='daksha_ebm_v1.0'
            ),
            RiskPrediction(
                gstin='27AABCU9603R1ZM',
                risk_probability=0.4200,
                risk_level='MEDIUM_RISK',
                top_driver_1='filing_delay_avg',
                top_driver_1_contribution=0.1200,
                top_driver_2='vendor_diversity',
                top_driver_2_contribution=0.0900,
                top_driver_3='avg_invoice_value',
                top_driver_3_contribution=0.0700,
                model_version='daksha_ebm_v1.0'
            ),
            RiskPrediction(
                gstin='07AABCU9603R1ZX',
                risk_probability=0.1500,
                risk_level='LOW_RISK',
                top_driver_1='transaction_count',
                top_driver_1_contribution=0.0500,
                top_driver_2='filing_gap',
                top_driver_2_contribution=0.0300,
                top_driver_3='seasonal_anomaly_score',
                top_driver_3_contribution=0.0200,
                model_version='daksha_ebm_v1.0'
            ),
        ]
        
        for pred in predictions:
            db.session.add(pred)
        
        # Create sample fraud patterns
        print("Creating sample fraud patterns...")
        patterns = [
            FraudPattern(
                pattern_type='circular_trade',
                gstin_list=['29AABCT1332L1Z5', '27AABCU9603R1ZM'],
                risk_score=0.8500,
                pattern_metadata={
                    'cycle_length': 3,
                    'total_value': 5000000,
                    'detection_confidence': 0.92
                }
            ),
            FraudPattern(
                pattern_type='ghost_invoice',
                gstin_list=['29AABCT1332L1Z5'],
                risk_score=0.7200,
                pattern_metadata={
                    'ghost_count': 15,
                    'total_value': 2500000,
                    'detection_confidence': 0.85
                }
            ),
            FraudPattern(
                pattern_type='spider_web',
                gstin_list=['29AABCT1332L1Z5', '27AABCU9603R1ZM', '07AABCU9603R1ZX'],
                risk_score=0.6800,
                pattern_metadata={
                    'hub_gstin': '29AABCT1332L1Z5',
                    'spoke_count': 12,
                    'detection_confidence': 0.78
                }
            ),
        ]
        
        for pattern in patterns:
            db.session.add(pattern)
        
        # Create sample audit narratives
        print("Creating sample audit narratives...")
        narratives = [
            AuditNarrative(
                gstin='29AABCT1332L1Z5',
                narrative_text="""HIGH RISK ALERT: Tech Solutions Pvt Ltd (29AABCT1332L1Z5)

Risk Score: 78.5%

Key Findings:
1. Payment Gap: Significant discrepancy between reported sales and actual payments received (25% contribution to risk)
2. Ghost Invoices: 15 suspicious invoices detected with no corresponding e-way bills (18% contribution)
3. Circular Trading: Involved in a 3-entity circular trade pattern with total value of ₹50 lakhs (15% contribution)

Recommendations:
- Immediate audit of payment records for Q4 2025
- Verification of all invoices without e-way bills
- Investigation of trading relationships with connected entities

This entity requires priority attention from the audit team."""
            ),
            AuditNarrative(
                gstin='27AABCU9603R1ZM',
                narrative_text="""MEDIUM RISK: Global Traders Inc (27AABCU9603R1ZM)

Risk Score: 42%

Key Findings:
1. Filing Delays: Average filing delay of 12 days beyond due date (12% contribution)
2. Vendor Diversity: Limited vendor base with high concentration (9% contribution)
3. Invoice Values: Unusual patterns in average invoice values (7% contribution)

Recommendations:
- Review filing compliance procedures
- Assess vendor relationship management
- Monitor invoice value trends

Standard monitoring recommended."""
            ),
        ]
        
        for narrative in narratives:
            db.session.add(narrative)
        
        # Create sample engineered features
        print("Creating sample engineered features...")
        features = [
            EngineeredFeatures(
                gstin='29AABCT1332L1Z5',
                payment_gap=1250000.00,
                payment_gap_pct=0.2500,
                ghost_invoice_pct=0.1200,
                shared_contact_flag=True,
                filing_gap=350000.00,
                excess_itc_flag=True,
                avg_invoice_value=125000.00,
                transaction_count=450,
                filing_delay_avg=8.5,
                circular_trade_involvement=3,
                spider_web_involvement=1,
                vendor_diversity=0.3500,
                buyer_concentration=0.6500,
                seasonal_anomaly_score=0.7800
            ),
            EngineeredFeatures(
                gstin='27AABCU9603R1ZM',
                payment_gap=250000.00,
                payment_gap_pct=0.0800,
                ghost_invoice_pct=0.0200,
                shared_contact_flag=False,
                filing_gap=50000.00,
                excess_itc_flag=False,
                avg_invoice_value=85000.00,
                transaction_count=320,
                filing_delay_avg=12.0,
                circular_trade_involvement=1,
                spider_web_involvement=0,
                vendor_diversity=0.4200,
                buyer_concentration=0.5500,
                seasonal_anomaly_score=0.3500
            ),
        ]
        
        for feature in features:
            db.session.add(feature)
        
        # Commit all changes
        db.session.commit()
        print("\n✅ Test data seeded successfully!")
        print("\nCreated:")
        print(f"  - {len(entities)} entities")
        print(f"  - {len(predictions)} risk predictions")
        print(f"  - {len(patterns)} fraud patterns")
        print(f"  - {len(narratives)} audit narratives")
        print(f"  - {len(features)} engineered features")
        print("\nYou can now:")
        print("  1. Sign up as Admin (no GSTIN required)")
        print("  2. Sign up as Business_Owner with GSTIN: 29AABCT1332L1Z5, 27AABCU9603R1ZM, or 07AABCU9603R1ZX")
        print("  3. Login and view the dashboard with sample data")

if __name__ == '__main__':
    seed_data()
