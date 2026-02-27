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

# Create tables logic
with app.app_context():
    db.create_all()

# Enable CORS for all routes, allowing the frontend to communicate
CORS(app)

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

if __name__ == '__main__':
    # Run the app on port 5000
    app.run(debug=True, port=5000)
