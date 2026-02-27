import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Try to import orchestration module, but don't fail if it's not available
try:
    from orchestration.llm_agent import execute_workflow_sync
    ORCHESTRATION_AVAILABLE = True
except ImportError:
    ORCHESTRATION_AVAILABLE = False
    execute_workflow_sync = None

from database import db
from auth import auth_bp, token_required, admin_required, get_secret_key

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure SQLite explicitly for dev
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///niyati.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = get_secret_key()

# Initialize DB
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')

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
    """Return RBAC‑filtered summary data used by the React
    dashboard page. This duplicates the logic found in
    ``app_fastapi.py`` but lives inside the Flask app so the
    existing demo frontend continues to function when the
    Flask server is running.
    """
    try:
        # RBAC filtering
        if current_user.role == 'Admin':
            risk_predictions = RiskPrediction.query.all()
        else:
            risk_predictions = RiskPrediction.query.filter_by(gstin=current_user.gstin).all()

        if not risk_predictions:
            return jsonify({'message': 'No dashboard data available'}), 404

        primary_pred = risk_predictions[0]
        health_score = 100 - (float(primary_pred.risk_probability) * 100)

        top_drivers = [
            {
                'feature': primary_pred.top_driver_1,
                'contribution': float(primary_pred.top_driver_1_contribution),
                'direction': 'positive' if primary_pred.top_driver_1_contribution > 0 else 'negative'
            },
            {
                'feature': primary_pred.top_driver_2,
                'contribution': float(primary_pred.top_driver_2_contribution),
                'direction': 'positive' if primary_pred.top_driver_2_contribution > 0 else 'negative'
            },
            {
                'feature': primary_pred.top_driver_3,
                'contribution': float(primary_pred.top_driver_3_contribution),
                'direction': 'positive' if primary_pred.top_driver_3_contribution > 0 else 'negative'
            }
        ]

        # vendor risks are not implemented in the Flask demo
        vendor_risks = []

        if current_user.role == 'Admin':
            patterns = FraudPattern.query.all()
        else:
            # SQLite / Postgres handling for JSON contains
            patterns = FraudPattern.query.filter(
                FraudPattern.gstin_list.contains([current_user.gstin])
            ).all()

        patterns_summary = {
            'circular_trade': len([p for p in patterns if p.pattern_type == 'circular_trade']),
            'ghost_invoices': len([p for p in patterns if p.pattern_type == 'ghost_invoice']),
            'spider_web_involvement': any(p.pattern_type == 'spider_web' for p in patterns)
        }

        return jsonify({
            'gstin': primary_pred.gstin,  # Add GSTIN to response
            'health_score': round(health_score, 2),
            'risk_level': primary_pred.risk_level,
            'risk_probability': float(primary_pred.risk_probability),
            'top_drivers': top_drivers,
            'vendor_risks': vendor_risks,
            'patterns': patterns_summary
        })

    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Create tables logic
with app.app_context():
    db.create_all()

# Enable CORS for all routes, allowing the frontend to communicate
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
    """
    Generic endpoint to handle inferences using the AI agent.
    Expects JSON payload with at least a 'prompt' field.
    """
    if not ORCHESTRATION_AVAILABLE:
        return jsonify({"error": "Orchestration module not available"}), 503
    
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' in request body."}), 400
        
        user_prompt = data.get('prompt')
        
        # Call the isolated ML/LLM logic
        # TODO: Implement proper prompt handling
        ai_result = {"message": "Orchestration workflow not yet implemented for prompts"}
        
        return jsonify({"data": ai_result})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/data', methods=['GET'])
@admin_required
def admin_data(current_user):
    """
    Admin-only endpoint to fetch sensitive or global data.
    """
    return jsonify({
        "message": "Welcome Admin!",
        "admin_email": current_user.email,
        "data": "This is highly sensitive data only accessible by admins."
    })

@app.route('/graph', methods=['GET'])
@token_required
def graph(current_user):
    """
    GET /graph - Return graph data from database (without Neo4j)
    
    Creates a simple graph from entity relationships in the database.
    """
    try:
        from models import EntityMaster, RiskPrediction
        
        # Get entities based on RBAC
        if current_user.role == 'Admin':
            entities = EntityMaster.query.all()
            risk_predictions = RiskPrediction.query.all()
        else:
            entities = EntityMaster.query.filter_by(gstin=current_user.gstin).all()
            risk_predictions = RiskPrediction.query.filter_by(gstin=current_user.gstin).all()
        
        # Create nodes from entities
        nodes = []
        for entity in entities:
            # Find risk level for this entity
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
        
        # Create edges from fraud patterns (circular trade indicates connections)
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
            # Create edges between entities in circular trade
            for i in range(len(gstin_list)):
                source = gstin_list[i]
                target = gstin_list[(i + 1) % len(gstin_list)]
                edges.append({
                    'source': source,
                    'target': target,
                    'type': 'CIRCULAR_TRADE'
                })
        
        return jsonify({
            'nodes': nodes,
            'edges': edges
        })
        
    except Exception as e:
        return jsonify({'message': str(e), 'nodes': [], 'edges': []}), 500

@app.route('/risk/<gstin>', methods=['GET'])
@token_required
def risk_details(current_user, gstin):
    """
    GET /risk/{gstin} - Return detailed risk data with SHAP plot information
    
    Provides risk predictions and top drivers for visualization.
    """
    try:
        # Check RBAC permissions
        if current_user.role != 'Admin' and current_user.gstin != gstin:
            return jsonify({'message': 'Access denied'}), 403
        
        from models import RiskPrediction, FraudPattern, AuditNarrative
        
        # Get risk prediction
        risk_pred = RiskPrediction.query.filter_by(gstin=gstin).first()
        
        if not risk_pred:
            return jsonify({'message': f'No risk data found for GSTIN {gstin}'}), 404
        
        # Get fraud patterns
        patterns = FraudPattern.query.filter(
            FraudPattern.gstin_list.contains([gstin])
        ).all()
        
        circular_trade_count = len([p for p in patterns if p.pattern_type == 'circular_trade'])
        ghost_invoice_count = len([p for p in patterns if p.pattern_type == 'ghost_invoice'])
        spider_web_involvement = any(p.pattern_type == 'spider_web' for p in patterns)
        
        # Get narrative
        narrative = AuditNarrative.query.filter_by(gstin=gstin).first()
        narrative_text = narrative.narrative_text if narrative else "No narrative available"
        
        # Build top drivers with baseline values for visualization
        top_drivers = [
            {
                'feature_name': risk_pred.top_driver_1,
                'contribution_weight': float(risk_pred.top_driver_1_contribution),
                'feature_value': float(risk_pred.top_driver_1_contribution) * 100,
                'baseline_value': 0.0,
                'direction': 'positive' if risk_pred.top_driver_1_contribution > 0 else 'negative'
            },
            {
                'feature_name': risk_pred.top_driver_2,
                'contribution_weight': float(risk_pred.top_driver_2_contribution),
                'feature_value': float(risk_pred.top_driver_2_contribution) * 100,
                'baseline_value': 0.0,
                'direction': 'positive' if risk_pred.top_driver_2_contribution > 0 else 'negative'
            },
            {
                'feature_name': risk_pred.top_driver_3,
                'contribution_weight': float(risk_pred.top_driver_3_contribution),
                'feature_value': float(risk_pred.top_driver_3_contribution) * 100,
                'baseline_value': 0.0,
                'direction': 'positive' if risk_pred.top_driver_3_contribution > 0 else 'negative'
            }
        ]
        
        return jsonify({
            'gstin': gstin,
            'risk_level': risk_pred.risk_level,
            'risk_probability': float(risk_pred.risk_probability),
            'top_drivers': top_drivers,
            'circular_trade_count': circular_trade_count,
            'ghost_invoice_count': ghost_invoice_count,
            'spider_web_involvement': spider_web_involvement,
            'narrative': narrative_text,
            'shape_plots': top_drivers  # Alias for compatibility
        })
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/logs/stream', methods=['GET'])
def logs_stream():
    """
    GET /logs/stream - Server-Sent Events endpoint for agent logs
    
    Returns a simple message since Flask doesn't have the full agent workflow.
    """
    def generate():
        yield f"data: Agent logs are only available with FastAPI backend\n\n"
        yield f"data: Current backend: Flask (limited features)\n\n"
        yield f"data: Switch to FastAPI for real-time agent monitoring\n\n"
    
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
    # Run the app on port 5000
    app.run(debug=True, port=5000)
