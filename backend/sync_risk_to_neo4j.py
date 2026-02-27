"""
Sync risk prediction data from SQLite to Neo4j

This script reads risk predictions from SQLite and updates
the corresponding Taxpayer nodes in Neo4j with risk information.
"""
import os
from dotenv import load_dotenv
from database import db
from models import RiskPrediction, EntityMaster, FraudPattern
from utils.db_connection import get_neo4j_connection
from flask import Flask

load_dotenv()

# Create Flask app for database context
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///niyati.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def sync_risk_data():
    """Sync risk prediction data from SQLite to Neo4j"""
    print("Starting risk data sync from SQLite to Neo4j...")
    
    with app.app_context():
        try:
            # Connect to Neo4j
            neo4j_conn = get_neo4j_connection()
            neo4j_conn.connect()
            print("✓ Connected to Neo4j")
            
            # Get all risk predictions from SQLite
            risk_predictions = RiskPrediction.query.all()
            print(f"✓ Found {len(risk_predictions)} risk predictions in SQLite")
            
            # Get all entities for business names
            entities = {e.gstin: e for e in EntityMaster.query.all()}
            print(f"✓ Found {len(entities)} entities in SQLite")
            
            # Get fraud patterns
            fraud_patterns = FraudPattern.query.all()
            circular_trade_gstins = set()
            for pattern in fraud_patterns:
                if pattern.pattern_type == 'circular_trade':
                    circular_trade_gstins.update(pattern.gstin_list)
            print(f"✓ Found {len(circular_trade_gstins)} GSTINs in circular trade")
            
            # Update Neo4j nodes
            updated_count = 0
            not_found_count = 0
            
            for pred in risk_predictions:
                gstin = pred.gstin
                entity = entities.get(gstin)
                business_name = entity.business_name if entity else gstin
                in_circular_trade = gstin in circular_trade_gstins
                
                # Update Taxpayer node in Neo4j
                update_query = """
                MATCH (t:Taxpayer {gstin: $gstin})
                SET 
                    t.business_name = $business_name,
                    t.risk_level = $risk_level,
                    t.risk_probability = $risk_probability,
                    t.in_circular_trade = $in_circular_trade,
                    t.last_transaction_date = $last_transaction_date
                RETURN t.gstin as gstin
                """
                
                params = {
                    'gstin': gstin,
                    'business_name': business_name,
                    'risk_level': pred.risk_level,
                    'risk_probability': float(pred.risk_probability),
                    'in_circular_trade': in_circular_trade,
                    'last_transaction_date': pred.predicted_at.isoformat() if pred.predicted_at else None
                }
                
                result = neo4j_conn.execute_query(update_query, params)
                
                if result:
                    updated_count += 1
                    if updated_count % 100 == 0:
                        print(f"  Updated {updated_count} nodes...")
                else:
                    not_found_count += 1
            
            neo4j_conn.close()
            
            print(f"\n✅ Sync completed!")
            print(f"  - Updated: {updated_count} nodes")
            print(f"  - Not found in Neo4j: {not_found_count} nodes")
            print(f"  - Total processed: {len(risk_predictions)} predictions")
            
        except Exception as e:
            print(f"\n❌ Error during sync: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    sync_risk_data()
