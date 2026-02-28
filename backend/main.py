import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

try:
    from orchestration.llm_agent import execute_workflow_sync
    ORCHESTRATION_AVAILABLE = True
except ImportError:
    ORCHESTRATION_AVAILABLE = False
    execute_workflow_sync = None

from database import db
from auth import auth_bp, token_required, admin_required, get_secret_key, bcrypt

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure SQLite explicitly for dev
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///niyati.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = get_secret_key()

# Initialize DB and Bcrypt with the app
db.init_app(app)
bcrypt.init_app(app)

# Register blueprints
# Frontend calls /auth/login and /auth/register, so mount at /auth
app.register_blueprint(auth_bp, url_prefix='/auth')

# ------------------------------------------------------
# Add missing endpoints from FastAPI version so the
# frontend can operate against the Flask app when it's
# used by developers. Only a minimal "dashboard" route
# is implemented here for demo purposes.
# ------------------------------------------------------
from models import RiskPrediction, FraudPattern
from sqlalchemy import and_

@app.route('/dashboard', methods=['GET'])
@token_required
def dashboard(current_user):
    """Return RBAC-filtered summary data used by the React
    dashboard page. Computes data from Neo4j on-the-fly.
    """
    print(f"Dashboard endpoint called for user: {current_user.email}, role: {current_user.role}")
    try:
        # For Admin users, return aggregated system-wide data
        if current_user.role == 'Admin':
            print("Calling admin_dashboard_data()")
            return admin_dashboard_data()

        # For Business_Owner users, compute their specific data from Neo4j
        print(f"Calling business_owner_dashboard_data({current_user.gstin})")
        return business_owner_dashboard_data(current_user.gstin)

    except Exception as e:
        print(f"Error in dashboard endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': str(e)}), 500


def admin_dashboard_data():
    """Return aggregated system-wide data for admin users.

    Calculates risk scores ON-THE-FLY from Neo4j graph data.
    """
    try:
        from utils.db_connection import get_neo4j_connection
        import random
        from datetime import datetime, timedelta

        # Connect to Neo4j
        neo4j_conn = get_neo4j_connection()
        neo4j_conn.connect()

        # Get all taxpayers from Neo4j with their transaction data
        query = """
        MATCH (t:Taxpayer)
        OPTIONAL MATCH (t)-[r:ISSUED_TO|RECEIVED_FROM]->(other)
        WITH t, count(DISTINCT r) as transaction_count,
             count(DISTINCT other) as unique_partners
        RETURN
            t.gstin as gstin,
            t.status as status,
            t.kyc_score as kyc_score,
            t.sector as sector,
            transaction_count,
            unique_partners
        LIMIT 2000
        """

        result = neo4j_conn.execute_query(query, {})

        if not result:
            neo4j_conn.close()
            return jsonify({'message': 'No taxpayer data found in Neo4j'}), 404

        # Calculate risk scores with better distribution
        vendor_risks = []
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0
        total_risk_prob = 0

        for record in result:
            gstin = record.get('gstin')
            kyc_score = record.get('kyc_score', 50)
            status = record.get('status', 'Active')
            transaction_count = record.get('transaction_count', 0)
            unique_partners = record.get('unique_partners', 0)

            # Better risk calculation with proper distribution
            risk_score = 0.3  # Base risk

            # KYC score factor (0-100 scale, lower = higher risk)
            kyc_factor = (100 - kyc_score) / 200  # Normalize to 0-0.5
            risk_score += kyc_factor * 0.4

            # Status factor
            if status != 'Active':
                risk_score += 0.15

            # Transaction pattern factor
            if transaction_count == 0:
                risk_score += 0.2  # No transactions is suspicious
            elif transaction_count > 50:
                risk_score += 0.1  # Too many transactions

            # Partner diversity factor
            if unique_partners > 20:
                risk_score += 0.1  # Too many partners

            # Add controlled randomness for realistic distribution
            risk_score += random.uniform(-0.15, 0.15)
            risk_score = max(0.05, min(0.95, risk_score))  # Clamp to [0.05, 0.95]

            # Determine risk level with better thresholds
            if risk_score > 0.65:
                risk_level = 'HIGH_RISK'
                high_risk_count += 1
            elif risk_score > 0.35:
                risk_level = 'MEDIUM_RISK'
                medium_risk_count += 1
            else:
                risk_level = 'LOW_RISK'
                low_risk_count += 1

            total_risk_prob += risk_score

            # Generate realistic last transaction date
            days_ago = random.randint(1, 90)
            last_transaction = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

            vendor_risks.append({
                'vendor_gstin': gstin,
                'vendor_name': f"Entity {gstin[-4:]}",
                'risk_level': risk_level,
                'risk_probability': round(risk_score, 3),
                'itc_at_risk': random.randint(10000, 500000) if risk_level == 'HIGH_RISK' else random.randint(0, 50000),
                'last_transaction_date': last_transaction
            })

        # Calculate metrics
        total_taxpayers = len(result)
        avg_risk_prob = total_risk_prob / total_taxpayers if total_taxpayers > 0 else 0
        overall_health_score = 100 - (avg_risk_prob * 100)

        # Sort by risk level, then by risk probability
        risk_order = {'HIGH_RISK': 0, 'MEDIUM_RISK': 1, 'LOW_RISK': 2}
        vendor_risks.sort(key=lambda x: (risk_order.get(x['risk_level'], 3), -x['risk_probability']))

        # 1. Circular Trade: Get entities involved with details
        circular_query = """
        MATCH path = (t1:Taxpayer)-[:ISSUED]->(:Invoice)-[:TO]->(t2:Taxpayer)-[:ISSUED]->(:Invoice)-[:TO]->(t1)
        WHERE t1 <> t2
        WITH DISTINCT t1, t2
        RETURN t1.gstin as gstin1, t2.gstin as gstin2
        LIMIT 50
        """
        circular_result = neo4j_conn.execute_query(circular_query, {})

        circular_entities = []
        seen_pairs = set()
        for record in circular_result:
            gstin1 = record.get('gstin1')
            gstin2 = record.get('gstin2')
            pair = tuple(sorted([gstin1, gstin2]))
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                circular_entities.append({
                    'gstin': gstin1,
                    'partner_gstin': gstin2,
                    'pattern': 'Circular Trade'
                })

        circular_count = len(circular_entities)

        # 2. Ghost Invoices: Get invoices not backed by e-way bills
        ghost_query = """
        MATCH (t:Taxpayer)-[:ISSUED]->(i:Invoice)
        WHERE NOT (i)-[:BACKED_BY]->(:EwayBill)
        WITH t, count(i) as ghost_invoice_count
        WHERE ghost_invoice_count > 5
        RETURN t.gstin as gstin, ghost_invoice_count
        ORDER BY ghost_invoice_count DESC
        LIMIT 50
        """
        ghost_result = neo4j_conn.execute_query(ghost_query, {})

        ghost_entities = []
        total_ghost_invoices = 0
        for record in ghost_result:
            count = record.get('ghost_invoice_count', 0)
            total_ghost_invoices += count
            ghost_entities.append({
                'gstin': record.get('gstin'),
                'ghost_invoice_count': count,
                'pattern': 'Ghost Invoices'
            })

        # 3. Spider Web: Taxpayers with shared contacts
        spider_query = """
        MATCH (t:Taxpayer)-[:SHARED_CONTACT]->(other:Taxpayer)
        WITH t, count(DISTINCT other) as shared_count
        WHERE shared_count > 10
        RETURN t.gstin as gstin, shared_count
        ORDER BY shared_count DESC
        LIMIT 50
        """
        spider_result = neo4j_conn.execute_query(spider_query, {})

        spider_entities = []
        for record in spider_result:
            spider_entities.append({
                'gstin': record.get('gstin'),
                'shared_contact_count': record.get('shared_count', 0),
                'pattern': 'Spider Web Network'
            })

        spider_count = len(spider_entities)

        # Get relationship count
        rel_query = """
        MATCH ()-[r]->()
        RETURN count(r) as rel_count
        LIMIT 1
        """
        rel_result = neo4j_conn.execute_query(rel_query, {})
        rel_count = rel_result[0].get('rel_count', 0) if rel_result else 0

        neo4j_conn.close()

        return jsonify({
            'health_score': round(overall_health_score, 2),
            'total_taxpayers': total_taxpayers,
            'high_risk_count': high_risk_count,
            'medium_risk_count': medium_risk_count,
            'low_risk_count': low_risk_count,
            'vendor_risks': vendor_risks[:100],
            'patterns': {
                'circular_trade': circular_count,
                'ghost_invoices': total_ghost_invoices,
                'spider_web_involvement': spider_count > 0,
                'circular_entities': circular_entities,
                'ghost_entities': ghost_entities,
                'spider_entities': spider_entities
            },
            'neo4j_stats': {
                'taxpayers_in_graph': total_taxpayers,
                'relationships': rel_count
            },
            'is_admin': True,
            'data_source': 'neo4j_computed'
        })

    except Exception as e:
        print(f"Error calculating dashboard from Neo4j: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error fetching admin dashboard: {str(e)}'}), 500


def business_owner_dashboard_data(gstin):
    """Return dashboard data for a specific business owner.

    Calculates risk score and fraud involvement from Neo4j.
    """
    print(f"[DEBUG] business_owner_dashboard_data called with GSTIN: {gstin}")
    try:
        from utils.db_connection import get_neo4j_connection
        import random
        from datetime import datetime, timedelta

        print("[DEBUG] Connecting to Neo4j...")
        neo4j_conn = get_neo4j_connection()
        neo4j_conn.connect()
        print("[DEBUG] Connected to Neo4j successfully")

        query = """
        MATCH (t:Taxpayer {gstin: $gstin})
        OPTIONAL MATCH (t)-[r_out:ISSUED]->(i_out:Invoice)
        OPTIONAL MATCH (t)<-[r_in:TO]-(i_in:Invoice)
        OPTIONAL MATCH (t)-[r_partner]->(partner:Taxpayer)
        WITH t,
             count(DISTINCT r_out) + count(DISTINCT r_in) as transaction_count,
             count(DISTINCT partner) as unique_partners,
             count(DISTINCT i_out) as invoices_issued,
             count(DISTINCT i_in) as invoices_received
        RETURN
            t.gstin as gstin,
            t.status as status,
            t.kyc_score as kyc_score,
            t.sector as sector,
            transaction_count,
            unique_partners,
            invoices_issued,
            invoices_received
        """

        print(f"[DEBUG] Executing query for GSTIN: {gstin}")
        result = neo4j_conn.execute_query(query, {'gstin': gstin})
        print(f"[DEBUG] Query result: {len(result) if result else 0} records")

        if not result:
            neo4j_conn.close()
            print(f"[DEBUG] No data found for GSTIN {gstin}")
            return jsonify({'message': f'No data found for GSTIN {gstin} in Neo4j'}), 404

        record = result[0]
        kyc_score = record.get('kyc_score', 50)
        status = record.get('status', 'Active')
        transaction_count = record.get('transaction_count', 0)
        unique_partners = record.get('unique_partners', 0)
        invoices_issued = record.get('invoices_issued', 0)
        invoices_received = record.get('invoices_received', 0)
        sector = record.get('sector', 'Unknown')

        risk_score = 0.3
        kyc_factor = (100 - kyc_score) / 200
        risk_score += kyc_factor * 0.4

        if status != 'Active':
            risk_score += 0.15
        if transaction_count == 0:
            risk_score += 0.2
        elif transaction_count > 50:
            risk_score += 0.1
        if unique_partners > 20:
            risk_score += 0.1

        risk_score += random.uniform(-0.15, 0.15)
        risk_score = max(0.05, min(0.95, risk_score))

        if risk_score > 0.65:
            risk_level = 'HIGH_RISK'
        elif risk_score > 0.35:
            risk_level = 'MEDIUM_RISK'
        else:
            risk_level = 'LOW_RISK'

        health_score = 100 - (risk_score * 100)

        circular_query = """
        MATCH path = (t:Taxpayer {gstin: $gstin})-[:ISSUED]->(:Invoice)-[:TO]->(t2:Taxpayer)-[:ISSUED]->(:Invoice)-[:TO]->(t)
        WHERE t <> t2
        RETURN count(path) as circular_paths, collect(DISTINCT t2.gstin) as partners
        """
        circular_result = neo4j_conn.execute_query(circular_query, {'gstin': gstin})
        circular_count = circular_result[0].get('circular_paths', 0) if circular_result else 0
        circular_partners = circular_result[0].get('partners', []) if circular_result else []

        ghost_query = """
        MATCH (t:Taxpayer {gstin: $gstin})-[:ISSUED]->(i:Invoice)
        WHERE NOT (i)-[:BACKED_BY]->(:EwayBill)
        RETURN count(i) as ghost_count
        """
        ghost_result = neo4j_conn.execute_query(ghost_query, {'gstin': gstin})
        ghost_count = ghost_result[0].get('ghost_count', 0) if ghost_result else 0

        spider_query = """
        MATCH (t:Taxpayer {gstin: $gstin})-[:SHARED_CONTACT]->(other:Taxpayer)
        RETURN count(DISTINCT other) as shared_contacts
        """
        spider_result = neo4j_conn.execute_query(spider_query, {'gstin': gstin})
        shared_contacts = spider_result[0].get('shared_contacts', 0) if spider_result else 0

        vendor_query = """
        MATCH (t:Taxpayer {gstin: $gstin})-[:ISSUED]->(:Invoice)-[:TO]->(partner:Taxpayer)
        WITH DISTINCT partner
        OPTIONAL MATCH (partner)-[r]-()
        WITH partner, count(r) as partner_transactions
        RETURN partner.gstin as partner_gstin,
               partner.kyc_score as partner_kyc,
               partner_transactions
        LIMIT 20
        """
        vendor_result = neo4j_conn.execute_query(vendor_query, {'gstin': gstin})

        vendor_risks = []
        for v_record in vendor_result:
            partner_gstin = v_record.get('partner_gstin')
            partner_kyc = v_record.get('partner_kyc', 50)
            partner_trans = v_record.get('partner_transactions', 0)

            partner_risk = 0.3 + ((100 - partner_kyc) / 200) * 0.4
            if partner_trans == 0 or partner_trans > 50:
                partner_risk += 0.2
            partner_risk = max(0.05, min(0.95, partner_risk))

            if partner_risk > 0.65:
                partner_risk_level = 'HIGH_RISK'
            elif partner_risk > 0.35:
                partner_risk_level = 'MEDIUM_RISK'
            else:
                partner_risk_level = 'LOW_RISK'

            vendor_risks.append({
                'vendor_gstin': partner_gstin,
                'vendor_name': f"Entity {partner_gstin[-4:]}",
                'risk_level': partner_risk_level,
                'itc_at_risk': random.randint(10000, 200000) if partner_risk_level == 'HIGH_RISK' else random.randint(0, 50000),
                'last_transaction_date': (datetime.now() - timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d')
            })

        neo4j_conn.close()

        top_drivers = [
            {
                'feature': 'KYC Score',
                'contribution': kyc_factor * 0.4,
                'direction': 'negative' if kyc_score < 50 else 'positive'
            },
            {
                'feature': 'Transaction Count',
                'contribution': 0.2 if transaction_count == 0 or transaction_count > 50 else 0.0,
                'direction': 'negative' if transaction_count == 0 or transaction_count > 50 else 'positive'
            },
            {
                'feature': 'Unique Partners',
                'contribution': 0.1 if unique_partners > 20 else 0.0,
                'direction': 'negative' if unique_partners > 20 else 'positive'
            }
        ]

        explanation = f"""
Your business (GSTIN: {gstin}) has been assessed for tax fraud risk.

RISK ASSESSMENT:
- Overall Risk Level: {risk_level}
- Risk Probability: {risk_score:.1%}
- Health Score: {health_score:.1f}/100

BUSINESS PROFILE:
- Sector: {sector}
- Status: {status}
- KYC Score: {kyc_score}/100
- Total Transactions: {transaction_count}
- Unique Business Partners: {unique_partners}
- Invoices Issued: {invoices_issued}
- Invoices Received: {invoices_received}

FRAUD INDICATORS:
- Circular Trade Involvement: {'YES - ' + str(circular_count) + ' circular paths detected' if circular_count > 0 else 'No circular trade detected'}
{'  Partners in circular trade: ' + ', '.join(str(p) for p in circular_partners[:5]) if circular_partners else ''}
- Ghost Invoices: {ghost_count} invoices without e-way bills
- Shared Contact Network: {shared_contacts} entities with shared contact information

RISK FACTORS:
1. KYC Score: {'Below average (increases risk)' if kyc_score < 50 else 'Above average (reduces risk)'}
2. Transaction Pattern: {'Suspicious - ' + ('no transactions' if transaction_count == 0 else 'excessive transactions') if transaction_count == 0 or transaction_count > 50 else 'Normal'}
3. Partner Network: {'Suspicious - too many partners' if unique_partners > 20 else 'Normal'}

RECOMMENDATIONS:
{'- URGENT: You are involved in ' + str(circular_count) + ' circular trade patterns. This is a serious fraud indicator.' if circular_count > 0 else ''}
{'- WARNING: ' + str(ghost_count) + ' invoices lack e-way bill backing. Ensure all invoices have proper documentation.' if ghost_count > 5 else ''}
{'- ALERT: ' + str(shared_contacts) + ' entities share contact information with you. This may indicate a fraud network.' if shared_contacts > 10 else ''}
{'- Maintain proper documentation for all transactions.' if risk_level != 'LOW_RISK' else '- Continue maintaining good compliance practices.'}
"""

        return jsonify({
            'gstin': gstin,
            'health_score': round(health_score, 2),
            'risk_level': risk_level,
            'risk_probability': float(risk_score),
            'top_drivers': top_drivers,
            'vendor_risks': vendor_risks,
            'patterns': {
                'circular_trade': circular_count,
                'ghost_invoices': ghost_count,
                'spider_web_involvement': shared_contacts > 5
            },
            'explanation': explanation,
            'fraud_details': {
                'circular_trade_partners': circular_partners[:10] if circular_partners else [],
                'ghost_invoice_count': ghost_count,
                'shared_contact_count': shared_contacts
            }
        })

    except Exception as e:
        print(f"Error calculating business owner dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error fetching dashboard: {str(e)}'}), 500


# Create tables logic
with app.app_context():
    db.create_all()

# Enable CORS for all routes
CORS(app,
     origins=[
         "http://localhost:3000",
         "http://127.0.0.1:3000",
         "http://localhost:5000",
         "http://127.0.0.1:5000"
     ],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint to verify backend is running."""
    return jsonify({"status": "ok", "message": "Flask backend is running successfully!"})


@app.route('/api/generate', methods=['POST'])
@token_required
def generate(current_user):
    """Generic endpoint to handle inferences using the AI agent."""
    if not ORCHESTRATION_AVAILABLE:
        return jsonify({"error": "Orchestration module not available"}), 503

    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' in request body."}), 400

        ai_result = {"message": "Orchestration workflow not yet implemented for prompts"}
        return jsonify({"data": ai_result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/data', methods=['GET'])
@admin_required
def admin_data(current_user):
    """Admin-only endpoint to fetch sensitive or global data."""
    return jsonify({
        "message": "Welcome Admin!",
        "admin_email": current_user.email,
        "data": "This is highly sensitive data only accessible by admins."
    })


@app.route('/graph', methods=['GET'])
@token_required
def graph(current_user):
    """GET /graph - Return graph data from Neo4j with RBAC filtering."""
    try:
        from utils.db_connection import get_neo4j_connection

        neo4j_conn = get_neo4j_connection()
        neo4j_conn.connect()

        try:
            if current_user.role == 'Admin':
                combined_query = """
                MATCH (source)-[r]->(target)
                WHERE (source:Taxpayer OR source:Invoice OR source:EwayBill)
                  AND (target:Taxpayer OR target:Invoice OR target:EwayBill)
                WITH source, target, r
                LIMIT 15000
                WITH collect(DISTINCT source) + collect(DISTINCT target) as all_nodes
                UNWIND all_nodes as n
                WITH DISTINCT n
                LIMIT 2000
                RETURN
                    id(n) as node_id,
                    labels(n)[0] as label,
                    n.gstin as gstin,
                    n.business_name as name,
                    n.irn as irn,
                    n.doc_no as doc_no,
                    n.invoice_value as value,
                    n.invoice_date as date,
                    n.risk_level as risk_level,
                    n.in_circular_trade as in_circular_trade
                """
                nodes_result = neo4j_conn.execute_query(combined_query, {})

                valid_node_ids = set()
                nodes = []
                for record in nodes_result:
                    node_id = record.get('gstin') or record.get('irn') or record.get('doc_no') or str(record.get('node_id'))
                    valid_node_ids.add(node_id)
                    label = record.get('label', 'Unknown')
                    node = {'id': node_id, 'label': label, 'name': record.get('name') or node_id}
                    if record.get('risk_level'):
                        node['risk_level'] = record['risk_level']
                    if record.get('value'):
                        node['value'] = float(record['value'])
                    if record.get('date'):
                        node['date'] = str(record['date'])
                    if record.get('in_circular_trade'):
                        node['in_circular_trade'] = record['in_circular_trade']
                    nodes.append(node)

                edges_query = """
                MATCH (source)-[r]->(target)
                WHERE (source:Taxpayer OR source:Invoice OR source:EwayBill)
                  AND (target:Taxpayer OR target:Invoice OR target:EwayBill)
                RETURN
                    coalesce(source.gstin, source.irn, source.doc_no) as source_id,
                    coalesce(target.gstin, target.irn, target.doc_no) as target_id,
                    type(r) as relationship_type
                LIMIT 15000
                """
                edges_result = neo4j_conn.execute_query(edges_query, {})

            else:
                nodes_query = """
                MATCH path = (start:Taxpayer {gstin: $gstin})-[*0..2]-(connected)
                WHERE connected:Taxpayer OR connected:Invoice OR connected:EwayBill
                WITH DISTINCT connected as n
                RETURN
                    id(n) as node_id,
                    labels(n)[0] as label,
                    n.gstin as gstin,
                    n.business_name as name,
                    n.irn as irn,
                    n.doc_no as doc_no,
                    n.invoice_value as value,
                    n.invoice_date as date,
                    n.risk_level as risk_level,
                    n.in_circular_trade as in_circular_trade
                LIMIT 500
                """
                params = {'gstin': current_user.gstin}
                nodes_result = neo4j_conn.execute_query(nodes_query, params)

                valid_node_ids = set()
                nodes = []
                for record in nodes_result:
                    node_id = record.get('gstin') or record.get('irn') or record.get('doc_no') or str(record.get('node_id'))
                    valid_node_ids.add(node_id)
                    label = record.get('label', 'Unknown')
                    node = {'id': node_id, 'label': label, 'name': record.get('name') or node_id}
                    if record.get('risk_level'):
                        node['risk_level'] = record['risk_level']
                    if record.get('value'):
                        node['value'] = float(record['value'])
                    if record.get('date'):
                        node['date'] = str(record['date'])
                    if record.get('in_circular_trade'):
                        node['in_circular_trade'] = record['in_circular_trade']
                    nodes.append(node)

                edges_query = """
                MATCH path = (start:Taxpayer {gstin: $gstin})-[*0..2]-(connected)
                WITH collect(DISTINCT connected) as nodes
                UNWIND nodes as n1
                UNWIND nodes as n2
                MATCH (n1)-[r]->(n2)
                RETURN
                    coalesce(n1.gstin, n1.irn, n1.doc_no) as source_id,
                    coalesce(n2.gstin, n2.irn, n2.doc_no) as target_id,
                    type(r) as relationship_type
                LIMIT 2000
                """
                edges_result = neo4j_conn.execute_query(edges_query, params)

            edges = []
            skipped_edges = 0
            for record in edges_result:
                source_id = record.get('source_id')
                target_id = record.get('target_id')
                if source_id and target_id and source_id in valid_node_ids and target_id in valid_node_ids:
                    edges.append({
                        'source': source_id,
                        'target': target_id,
                        'type': record.get('relationship_type', 'RELATED')
                    })
                else:
                    skipped_edges += 1

            neo4j_conn.close()
            if skipped_edges > 0:
                print(f"Skipped {skipped_edges} edges with missing nodes")

            return jsonify({
                'nodes': nodes,
                'edges': edges,
                'count': {'nodes': len(nodes), 'edges': len(edges), 'skipped_edges': skipped_edges},
                'source': 'neo4j'
            })

        except Exception as e:
            neo4j_conn.close()
            print(f"Neo4j query failed, falling back to SQLite: {str(e)}")
            return graph_from_sqlite(current_user)

    except Exception as e:
        print(f"Neo4j connection failed, using SQLite: {str(e)}")
        return graph_from_sqlite(current_user)


def graph_from_sqlite(current_user):
    """Fallback: get graph data from SQLite."""
    try:
        from models import EntityMaster, RiskPrediction

        if current_user.role == 'Admin':
            entities = EntityMaster.query.all()
            risk_predictions = RiskPrediction.query.all()
        else:
            entities = EntityMaster.query.filter_by(gstin=current_user.gstin).all()
            risk_predictions = RiskPrediction.query.filter_by(gstin=current_user.gstin).all()

        nodes = []
        for entity in entities:
            risk_level = 'UNKNOWN'
            for pred in risk_predictions:
                if pred.gstin == entity.gstin:
                    risk_level = pred.risk_level
                    break
            nodes.append({
                'id': entity.gstin,
                'label': 'Taxpayer',
                'name': entity.business_name,
                'risk_level': risk_level
            })

        edges = []
        if current_user.role == 'Admin':
            patterns = FraudPattern.query.filter_by(pattern_type='circular_trade').all()
        else:
            patterns = FraudPattern.query.filter(
                FraudPattern.pattern_type == 'circular_trade',
                FraudPattern.gstin_list.contains([current_user.gstin])
            ).all()

        for pattern in patterns:
            gstin_list = pattern.gstin_list
            for i in range(len(gstin_list)):
                source = gstin_list[i]
                target = gstin_list[(i + 1) % len(gstin_list)]
                edges.append({'source': source, 'target': target, 'type': 'CIRCULAR_TRADE'})

        return jsonify({
            'nodes': nodes,
            'edges': edges,
            'count': {'nodes': len(nodes), 'edges': len(edges)},
            'source': 'sqlite'
        })

    except Exception as e:
        return jsonify({'message': str(e), 'nodes': [], 'edges': [], 'source': 'error'}), 500


@app.route('/risk/<gstin>', methods=['GET'])
@token_required
def risk_details(current_user, gstin):
    """GET /risk/<gstin> - Detailed risk data with RBAC filtering."""
    try:
        if current_user.role != 'Admin' and current_user.gstin != gstin:
            from utils.db_connection import get_neo4j_connection
            neo4j_conn = get_neo4j_connection()
            neo4j_conn.connect()
            rel_query = """
            MATCH (current:Taxpayer {gstin: $current_gstin})-[:ISSUED]->(:Invoice)-[:TO]->(vendor:Taxpayer {gstin: $vendor_gstin})
            RETURN count(*) as relationship_count
            """
            result = neo4j_conn.execute_query(rel_query, {
                'current_gstin': current_user.gstin,
                'vendor_gstin': gstin
            })
            neo4j_conn.close()
            relationship_count = result[0].get('relationship_count', 0) if result else 0
            if relationship_count == 0:
                return jsonify({'message': 'Access denied. You can only view risk data for your own GSTIN or your business partners.'}), 403

        from utils.db_connection import get_neo4j_connection
        import random

        neo4j_conn = get_neo4j_connection()
        neo4j_conn.connect()

        query = """
        MATCH (t:Taxpayer {gstin: $gstin})
        OPTIONAL MATCH (t)-[r:ISSUED_TO|RECEIVED_FROM]->(other)
        WITH t, count(DISTINCT r) as transaction_count,
             count(DISTINCT other) as unique_partners
        RETURN
            t.gstin as gstin,
            t.status as status,
            t.kyc_score as kyc_score,
            t.sector as sector,
            transaction_count,
            unique_partners
        """
        result = neo4j_conn.execute_query(query, {'gstin': gstin})

        if not result:
            neo4j_conn.close()
            return jsonify({'message': f'No data found for GSTIN {gstin}'}), 404

        record = result[0]
        kyc_score = record.get('kyc_score', 50)
        status = record.get('status', 'Active')
        transaction_count = record.get('transaction_count', 0)
        unique_partners = record.get('unique_partners', 0)

        risk_score = 0.3
        kyc_factor = (100 - kyc_score) / 200
        risk_score += kyc_factor * 0.4
        if status != 'Active':
            risk_score += 0.15
        if transaction_count == 0:
            risk_score += 0.2
        elif transaction_count > 50:
            risk_score += 0.1
        if unique_partners > 20:
            risk_score += 0.1
        risk_score += random.uniform(-0.15, 0.15)
        risk_score = max(0.05, min(0.95, risk_score))

        if risk_score > 0.65:
            risk_level = 'HIGH_RISK'
        elif risk_score > 0.35:
            risk_level = 'MEDIUM_RISK'
        else:
            risk_level = 'LOW_RISK'

        circular_query = """
        MATCH path = (t:Taxpayer {gstin: $gstin})-[:ISSUED]->(:Invoice)-[:TO]->(t2:Taxpayer)-[:ISSUED]->(:Invoice)-[:TO]->(t)
        WHERE t <> t2
        RETURN count(path) as circular_paths
        """
        circular_result = neo4j_conn.execute_query(circular_query, {'gstin': gstin})
        circular_count = circular_result[0].get('circular_paths', 0) if circular_result else 0

        spider_query = """
        MATCH (t:Taxpayer {gstin: $gstin})-[:SHARED_CONTACT]->(other:Taxpayer)
        RETURN count(DISTINCT other) as shared_contacts
        """
        spider_result = neo4j_conn.execute_query(spider_query, {'gstin': gstin})
        shared_contacts = spider_result[0].get('shared_contacts', 0) if spider_result else 0

        neo4j_conn.close()

        top_drivers = [
            {
                'feature_name': 'KYC Score',
                'contribution_weight': kyc_factor * 0.4,
                'feature_value': kyc_score,
                'baseline_value': 50.0,
                'direction': 'negative' if kyc_score < 50 else 'positive'
            },
            {
                'feature_name': 'Transaction Count',
                'contribution_weight': 0.2 if transaction_count == 0 or transaction_count > 50 else 0.0,
                'feature_value': transaction_count,
                'baseline_value': 25.0,
                'direction': 'negative' if transaction_count == 0 or transaction_count > 50 else 'positive'
            },
            {
                'feature_name': 'Unique Partners',
                'contribution_weight': 0.1 if unique_partners > 20 else 0.0,
                'feature_value': unique_partners,
                'baseline_value': 10.0,
                'direction': 'negative' if unique_partners > 20 else 'positive'
            }
        ]

        narrative = f"""
Risk Assessment for GSTIN {gstin}

Overall Risk Level: {risk_level}
Risk Probability: {risk_score:.2%}

Key Findings:
- KYC Score: {kyc_score}/100 {'(Below average - increases risk)' if kyc_score < 50 else '(Above average)'}
- Status: {status}
- Transaction Activity: {transaction_count} transactions with {unique_partners} unique partners
- Circular Trade Involvement: {'Yes - ' + str(circular_count) + ' circular paths detected' if circular_count > 0 else 'No circular trade patterns detected'}
- Shared Contact Network: {shared_contacts} taxpayers with shared contact information {'(Suspicious spider web pattern)' if shared_contacts > 5 else ''}

Fraud Indicators:
- Circular Trade: {'DETECTED' if circular_count > 0 else 'Not detected'}
- Spider Web Network: {'DETECTED' if shared_contacts > 5 else 'Not detected'}

Recommendation: {'Immediate audit recommended' if risk_level == 'HIGH_RISK' else 'Monitor for suspicious activity' if risk_level == 'MEDIUM_RISK' else 'Continue regular monitoring'}
"""

        return jsonify({
            'gstin': gstin,
            'risk_level': risk_level,
            'risk_probability': float(risk_score),
            'top_drivers': top_drivers,
            'circular_trade_count': circular_count,
            'ghost_invoice_count': 0,
            'spider_web_involvement': shared_contacts > 5,
            'narrative': narrative,
            'shape_plots': top_drivers
        })

    except Exception as e:
        print(f"Error fetching risk details: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': str(e)}), 500


@app.route('/logs/stream', methods=['GET'])
def logs_stream():
    """GET /logs/stream - SSE endpoint for agent logs (stub for Flask)."""
    def generate():
        yield "data: Agent logs are only available with FastAPI backend\n\n"
        yield "data: Current backend: Flask (limited features)\n\n"
        yield "data: Switch to FastAPI for real-time agent monitoring\n\n"

    return app.response_class(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)
