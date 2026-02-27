"""
FastAPI Application for Project Niyati

This module implements the REST API endpoints for the GST fraud detection platform.
It includes SSE support for real-time agent progress updates, authentication, RBAC,
and integration with the LangGraph multi-agent workflow.

Requirements: 11.1-11.8, 19.1-19.2, 17.7
"""

import os
import asyncio
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from queue import Queue

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import pandas as pd
import jwt
from dotenv import load_dotenv

# Import database and models
from database import db
from models import User
from flask import Flask as FlaskApp
from flask_bcrypt import Bcrypt

# Import RBAC utilities
from rbac import (
    apply_neo4j_tenant_filter,
    apply_postgres_tenant_filter,
    check_access_permission,
    rbac_error_handler
)

# Import orchestration
from orchestration.llm_agent import execute_workflow, set_event_queue

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Project Niyati API",
    description="Real-time GST Intelligence & Fraud Detection Platform",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Initialize Flask app for SQLAlchemy (compatibility layer)
flask_app = FlaskApp(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///niyati.db')
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
flask_app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'my-super-secret-niyati-key')
db.init_app(flask_app)
bcrypt = Bcrypt(flask_app)

# Create tables
with flask_app.app_context():
    db.create_all()

# Global event queue for SSE
event_queue: Optional[asyncio.Queue] = None

# Security
security = HTTPBearer()


def get_secret_key() -> str:
    """Get JWT secret key from environment"""
    return os.environ.get('JWT_SECRET_KEY', 'my-super-secret-niyati-key')


# Pydantic models for request/response validation
class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class RegisterRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    role: str = Field(..., description="User role (Admin or Business_Owner)")
    gstin: Optional[str] = Field(None, description="GSTIN for Business_Owner")


class PreAuditRequest(BaseModel):
    gstin: str = Field(..., description="GSTIN to audit", min_length=15, max_length=15)


class TokenData(BaseModel):
    user_id: int
    role: str
    gstin: Optional[str]


# Dependency: Get current user from JWT token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Extract and validate JWT token, return current user.
    
    Requirements: 8.2
    """
    token = credentials.credentials
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, get_secret_key(), algorithms=["HS256"])
        user_id = payload.get('user_id')
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id"
            )
        
        # Query user from database
        with flask_app.app_context():
            user = User.query.filter_by(id=user_id).first()
            
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # Attach token claims to user object
            user.token_role = payload.get('role')
            user.token_gstin = payload.get('gstin')
            
            return user
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# Dependency: Require admin role
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensure current user has Admin role.
    
    Requirements: 8.3
    """
    if current_user.role != 'Admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ============================================================================
# TASK 12.1: SSE Streaming Endpoint
# ============================================================================

async def broadcast_event(message: str):
    """
    Broadcast an event message to all SSE clients.
    
    Requirements: 19.2
    """
    global event_queue
    if event_queue is not None:
        await event_queue.put(message)


async def event_generator():
    """
    Generate Server-Sent Events from the global event queue.
    
    Requirements: 19.1
    """
    global event_queue
    
    # Create a new queue for this client
    event_queue = asyncio.Queue()
    
    # Set the event queue for the orchestration layer
    set_event_queue(event_queue)
    
    try:
        while True:
            # Wait for events from the queue
            message = await event_queue.get()
            
            # Format as SSE
            yield f"data: {message}\n\n"
            
    except asyncio.CancelledError:
        logger.info("SSE client disconnected")


@app.get("/logs/stream")
async def stream_logs():
    """
    GET /logs/stream - Server-Sent Events endpoint for real-time agent logs.
    
    This endpoint streams real-time progress updates from all 5 agents during
    workflow execution. Clients can connect to this endpoint to receive live
    updates about data processing, graph construction, pattern detection, etc.
    
    Returns:
        StreamingResponse with text/event-stream content type
    
    Requirements: 19.1, 19.2
    """
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# ============================================================================
# TASK 12.9: Error Handling Middleware
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions and return consistent error responses.
    
    Requirements: 11.7
    """
    logger.error(f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle internal server errors and return generic error response.
    
    Requirements: 11.8
    """
    logger.error(f"Internal error: {str(exc)} - Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error"}
    )


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    POST /auth/register - User registration endpoint.
    
    Requirements: 8.1, 11.5
    """
    # Validate role
    if request.role not in ['Admin', 'Business_Owner']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be Admin or Business_Owner"
        )
    
    with flask_app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email=request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists"
            )
        
        # Hash password
        password_hash = bcrypt.generate_password_hash(request.password).decode('utf-8')
        
        # Create new user
        new_user = User(
            email=request.email,
            password_hash=password_hash,
            role=request.role,
            gstin=request.gstin
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            return {"message": "User registered successfully"}
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error registering user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error registering user"
            )


@app.post("/auth/login")
async def login(request: LoginRequest):
    """
    POST /auth/login - User authentication endpoint.
    
    Requirements: 11.6
    """
    with flask_app.app_context():
        # Find user
        user = User.query.filter_by(email=request.email).first()
        
        if not user or not bcrypt.check_password_hash(user.password_hash, request.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Generate JWT token
        from datetime import datetime, timedelta
        token = jwt.encode({
            'user_id': user.id,
            'role': user.role,
            'gstin': user.gstin,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, get_secret_key(), algorithm="HS256")
        
        return {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "gstin": user.gstin
            }
        }


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "FastAPI backend is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ============================================================================
# TASK 12.2: POST /sync Endpoint
# ============================================================================

@app.post("/sync")
async def sync_data(
    e_invoices: UploadFile = File(...),
    eway_bills: UploadFile = File(...),
    entity_master: UploadFile = File(...),
    filing_history: UploadFile = File(...),
    purchase_register: UploadFile = File(...),
    returns_summary: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    POST /sync - Upload 6 CSV files and trigger full workflow.
    
    This endpoint accepts multipart/form-data with 6 CSV files, triggers the
    complete LangGraph workflow (all 5 agents), and returns a summary of results.
    
    Requirements: 11.1, 7.7
    """
    try:
        # Read CSV files into pandas DataFrames
        csv_files = {}
        
        for file, name in [
            (e_invoices, 'e_invoices'),
            (eway_bills, 'eway_bills'),
            (entity_master, 'entity_master'),
            (filing_history, 'filing_history'),
            (purchase_register, 'purchase_register'),
            (returns_summary, 'returns_summary')
        ]:
            # Validate file type
            if not file.filename.endswith('.csv'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid file type for {name}. Must be CSV"
                )
            
            # Read CSV content
            content = await file.read()
            
            try:
                df = pd.read_csv(pd.io.common.BytesIO(content))
                csv_files[name] = df
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error parsing {name}: {str(e)}"
                )
        
        # Execute workflow
        result = await execute_workflow(csv_files)
        
        # Check if workflow failed
        if result.get('status') == 'failed':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Workflow failed: {', '.join(result.get('errors', []))}"
            )
        
        # Return summary response
        return {
            "status": "success",
            "message": "Workflow completed successfully",
            "summary": result.get('summary', {}),
            "execution_time_seconds": result.get('execution_time_seconds', 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /sync endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing CSV files"
        )


# ============================================================================
# TASK 12.3: POST /pre-audit Endpoint
# ============================================================================

@app.post("/pre-audit")
async def pre_audit(
    request: PreAuditRequest,
    current_user: User = Depends(get_current_user)
):
    """
    POST /pre-audit - Trigger on-demand fraud check for specific GSTIN.
    
    This endpoint executes the full agent workflow for a specific GSTIN only,
    returns detailed risk analysis, sends email notification for HIGH_RISK cases,
    and logs the request.
    
    Requirements: 11.2, 10.1, 10.2, 10.3, 10.4
    """
    try:
        # Check RBAC permissions
        try:
            check_access_permission(current_user.role, current_user.gstin, request.gstin)
        except PermissionError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        
        # TODO: Execute workflow for specific GSTIN
        # This requires filtering the CSV data to only include records for the requested GSTIN
        # For now, return a placeholder response
        
        # Query risk predictions from database
        with flask_app.app_context():
            from models import RiskPrediction, FraudPattern, AuditNarrative
            
            # Get risk prediction
            risk_pred = RiskPrediction.query.filter_by(gstin=request.gstin).first()
            
            if not risk_pred:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No risk data found for GSTIN {request.gstin}"
                )
            
            # Get structural patterns
            patterns = FraudPattern.query.filter(
                FraudPattern.gstin_list.contains([request.gstin])
            ).all()
            
            circular_trade_count = len([p for p in patterns if p.pattern_type == 'circular_trade'])
            ghost_invoice_count = len([p for p in patterns if p.pattern_type == 'ghost_invoice'])
            spider_web_involvement = any(p.pattern_type == 'spider_web' for p in patterns)
            
            # Get narrative
            narrative = AuditNarrative.query.filter_by(gstin=request.gstin).first()
            narrative_text = narrative.narrative_text if narrative else "No narrative available"
            
            # Build response
            response = {
                "gstin": request.gstin,
                "risk_level": risk_pred.risk_level,
                "risk_probability": float(risk_pred.risk_probability),
                "top_drivers": [
                    {
                        "feature": risk_pred.top_driver_1,
                        "contribution": float(risk_pred.top_driver_1_contribution),
                        "direction": "positive" if risk_pred.top_driver_1_contribution > 0 else "negative"
                    },
                    {
                        "feature": risk_pred.top_driver_2,
                        "contribution": float(risk_pred.top_driver_2_contribution),
                        "direction": "positive" if risk_pred.top_driver_2_contribution > 0 else "negative"
                    },
                    {
                        "feature": risk_pred.top_driver_3,
                        "contribution": float(risk_pred.top_driver_3_contribution),
                        "direction": "positive" if risk_pred.top_driver_3_contribution > 0 else "negative"
                    }
                ],
                "circular_trade_count": circular_trade_count,
                "ghost_invoice_count": ghost_invoice_count,
                "spider_web_involvement": spider_web_involvement,
                "narrative": narrative_text
            }
            
            # Send email notification if HIGH_RISK (Requirement 10.3)
            if risk_pred.risk_level == 'HIGH_RISK':
                # TODO: Implement email notification
                logger.info(f"HIGH_RISK detected for {request.gstin} - Email notification should be sent")
            
            # Log request (Requirement 10.4)
            logger.info(f"Pre-audit request: user_id={current_user.id}, gstin={request.gstin}, "
                       f"risk_level={risk_pred.risk_level}, timestamp={datetime.utcnow()}")
            
            return response
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /pre-audit endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing pre-audit request"
        )


# ============================================================================
# TASK 12.5: GET /dashboard Endpoint with RBAC
# ============================================================================

@app.get("/dashboard")
async def get_dashboard(current_user: User = Depends(get_current_user)):
    """
    GET /dashboard - Retrieve dashboard data with RBAC filtering.
    
    This endpoint returns health score, risk level, top drivers, vendor risks,
    and detected patterns. Data is filtered based on user role and GSTIN.
    
    Requirements: 11.3, 9.2, 17.7
    """
    try:
        with flask_app.app_context():
            from models import RiskPrediction, FraudPattern, EngineeredFeatures
            
            # Apply RBAC filtering
            if current_user.role == 'Admin':
                # Admin sees all data
                risk_predictions = RiskPrediction.query.all()
            else:
                # Business_Owner sees only their GSTIN
                risk_predictions = RiskPrediction.query.filter_by(gstin=current_user.gstin).all()
            
            if not risk_predictions:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No dashboard data available"
                )
            
            # Get primary risk prediction (first one or user's GSTIN)
            primary_pred = risk_predictions[0]
            
            # Compute health score (Requirement 9.2)
            health_score = 100 - (float(primary_pred.risk_probability) * 100)
            
            # Get top drivers
            top_drivers = [
                {
                    "feature": primary_pred.top_driver_1,
                    "contribution": float(primary_pred.top_driver_1_contribution),
                    "direction": "positive" if primary_pred.top_driver_1_contribution > 0 else "negative"
                },
                {
                    "feature": primary_pred.top_driver_2,
                    "contribution": float(primary_pred.top_driver_2_contribution),
                    "direction": "positive" if primary_pred.top_driver_2_contribution > 0 else "negative"
                },
                {
                    "feature": primary_pred.top_driver_3,
                    "contribution": float(primary_pred.top_driver_3_contribution),
                    "direction": "positive" if primary_pred.top_driver_3_contribution > 0 else "negative"
                }
            ]
            
            # Get vendor risks
            # TODO: Implement vendor risk query from database
            vendor_risks = []
            
            # Get patterns
            if current_user.role == 'Admin':
                patterns = FraudPattern.query.all()
            else:
                patterns = FraudPattern.query.filter(
                    FraudPattern.gstin_list.contains([current_user.gstin])
                ).all()
            
            patterns_summary = {
                "circular_trade": len([p for p in patterns if p.pattern_type == 'circular_trade']),
                "ghost_invoices": len([p for p in patterns if p.pattern_type == 'ghost_invoice']),
                "spider_web_involvement": any(p.pattern_type == 'spider_web' for p in patterns)
            }
            
            return {
                "health_score": round(health_score, 2),
                "risk_level": primary_pred.risk_level,
                "risk_probability": float(primary_pred.risk_probability),
                "top_drivers": top_drivers,
                "vendor_risks": vendor_risks,
                "patterns": patterns_summary
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /dashboard endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving dashboard data"
        )


# ============================================================================
# TASK 12.7: GET /graph Endpoint with RBAC
# ============================================================================

@app.get("/graph")
async def get_graph(current_user: User = Depends(get_current_user)):
    """
    GET /graph - Retrieve graph visualization data with RBAC filtering.
    
    This endpoint queries Neo4j for nodes and edges, applies RBAC filtering,
    and returns data formatted for force-directed graph visualization.
    
    Requirements: 11.4, 17.7
    """
    try:
        from neo4j import GraphDatabase
        
        # Connect to Neo4j
        neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
        neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
        neo4j_password = os.environ.get('NEO4J_PASSWORD', 'password')
        
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        with driver.session() as session:
            # Query for nodes and edges
            if current_user.role == 'Admin':
                # Admin sees all nodes
                nodes_query = """
                MATCH (t:Taxpayer)
                OPTIONAL MATCH (t)-[:ISSUED]->(i:Invoice)
                RETURN t.gstin as id, 'Taxpayer' as label, t.business_name as name,
                       COALESCE(t.risk_level, 'UNKNOWN') as risk_level
                LIMIT 1000
                """
                nodes_result = session.run(nodes_query)
                
                edges_query = """
                MATCH (t1:Taxpayer)-[:ISSUED]->(i:Invoice)-[:TO]->(t2:Taxpayer)
                RETURN t1.gstin as source, t2.gstin as target, 'TRANSACTION' as type
                LIMIT 1000
                """
                edges_result = session.run(edges_query)
                
            else:
                # Business_Owner sees only their network
                nodes_query = """
                MATCH (t:Taxpayer {gstin: $gstin})
                OPTIONAL MATCH (t)-[:ISSUED]->(i:Invoice)-[:TO]->(t2:Taxpayer)
                OPTIONAL MATCH (t3:Taxpayer)-[:ISSUED]->(i2:Invoice)-[:TO]->(t)
                WITH collect(DISTINCT t) + collect(DISTINCT t2) + collect(DISTINCT t3) as taxpayers
                UNWIND taxpayers as taxpayer
                RETURN taxpayer.gstin as id, 'Taxpayer' as label, 
                       taxpayer.business_name as name,
                       COALESCE(taxpayer.risk_level, 'UNKNOWN') as risk_level
                """
                nodes_result = session.run(nodes_query, gstin=current_user.gstin)
                
                edges_query = """
                MATCH (t1:Taxpayer)-[:ISSUED]->(i:Invoice)-[:TO]->(t2:Taxpayer)
                WHERE t1.gstin = $gstin OR t2.gstin = $gstin
                RETURN t1.gstin as source, t2.gstin as target, 'TRANSACTION' as type
                """
                edges_result = session.run(edges_query, gstin=current_user.gstin)
            
            # Format nodes
            nodes = []
            for record in nodes_result:
                nodes.append({
                    "id": record["id"],
                    "label": record["label"],
                    "name": record["name"],
                    "risk_level": record["risk_level"]
                })
            
            # Format edges
            edges = []
            for record in edges_result:
                edges.append({
                    "source": record["source"],
                    "target": record["target"],
                    "type": record["type"]
                })
            
            driver.close()
            
            return {
                "nodes": nodes,
                "edges": edges
            }
            
    except Exception as e:
        logger.error(f"Error in /graph endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving graph data"
        )


# ============================================================================
# TASK 12.8: GET /risk/{gstin} Endpoint with Shape Plot Data
# ============================================================================

@app.get("/risk/{gstin}")
async def get_risk_details(
    gstin: str,
    current_user: User = Depends(get_current_user)
):
    """
    GET /risk/{gstin} - Retrieve detailed risk data with shape plots.
    
    This endpoint returns risk predictions with EBM shape plot data for
    visualization of feature contributions. RBAC filtering is applied.
    
    Requirements: 20.1, 20.2, 20.3, 20.4
    """
    try:
        # Check RBAC permissions
        try:
            check_access_permission(current_user.role, current_user.gstin, gstin)
        except PermissionError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        
        with flask_app.app_context():
            from models import RiskPrediction, ShapePlot
            
            # Get risk prediction
            risk_pred = RiskPrediction.query.filter_by(gstin=gstin).first()
            
            if not risk_pred:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No risk data found for GSTIN {gstin}"
                )
            
            # Get shape plots
            shape_plots = ShapePlot.query.filter_by(gstin=gstin).all()
            
            # Format shape plot data
            shape_plots_data = []
            for plot in shape_plots:
                shape_plots_data.append({
                    "feature_name": plot.feature_name,
                    "contribution_weight": float(plot.contribution_weight),
                    "feature_value": float(plot.feature_value),
                    "baseline_value": float(plot.baseline_value),
                    "x_values": plot.x_values,  # JSON array
                    "y_values": plot.y_values   # JSON array
                })
            
            return {
                "gstin": gstin,
                "risk_level": risk_pred.risk_level,
                "risk_probability": float(risk_pred.risk_probability),
                "top_drivers": [
                    {
                        "feature": risk_pred.top_driver_1,
                        "contribution": float(risk_pred.top_driver_1_contribution),
                        "direction": "positive" if risk_pred.top_driver_1_contribution > 0 else "negative"
                    },
                    {
                        "feature": risk_pred.top_driver_2,
                        "contribution": float(risk_pred.top_driver_2_contribution),
                        "direction": "positive" if risk_pred.top_driver_2_contribution > 0 else "negative"
                    },
                    {
                        "feature": risk_pred.top_driver_3,
                        "contribution": float(risk_pred.top_driver_3_contribution),
                        "direction": "positive" if risk_pred.top_driver_3_contribution > 0 else "negative"
                    }
                ],
                "shape_plots": shape_plots_data
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /risk/{gstin} endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving risk details"
        )
