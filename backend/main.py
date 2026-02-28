"""
FastAPI Application for Project Niyati

This module implements the REST API endpoints for the GST fraud detection platform.
It includes SSE support for real-time agent progress updates, authentication, RBAC,
and integration with the LangGraph multi-agent workflow.
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

# Enable CORS — read allowed origins from environment for production
_default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
]
_env_origins = os.environ.get("CORS_ORIGINS", "")
_cors_origins = [o.strip() for o in _env_origins.split(",") if o.strip()] if _env_origins else _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# Health check for Cloud Run / load balancers
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Initialize Flask app for SQLAlchemy (compatibility layer)
flask_app = FlaskApp(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///niyati.db')
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
flask_app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET', 'my-super-secret-niyati-key')
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
    return os.environ.get('JWT_SECRET', 'my-super-secret-niyati-key')


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


class LiveFileRequest(BaseModel):
    seller_gstin: str = Field(..., description="Seller GSTIN (15-char)")
    buyer_gstin: str = Field(..., description="Buyer GSTIN (15-char)")
    amount: float = Field(..., description="Invoice amount in INR", gt=0)
    tax: float = Field(0.0, description="Tax amount in INR", ge=0)
    hsn_code: Optional[str] = Field(None, description="HSN/SAC code")


# Dependency: Get current user from JWT token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Extract and validate JWT token, return current user.
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
    """
    global event_queue
    if event_queue is not None:
        await event_queue.put(message)


async def event_generator():
    """
    Generate Server-Sent Events from the global event queue.
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
    """
    # Validate role
    if request.role not in ['Admin', 'Business_Owner']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be Admin or Business_Owner"
        )
    
    # Admin registration guard: only allow Admin if no admins exist yet
    if request.role == 'Admin':
        with flask_app.app_context():
            existing_admins = User.query.filter_by(role='Admin').count()
            if existing_admins > 0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin registration is restricted. An admin account already exists."
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
    current_user: User = Depends(require_admin)
):
    """
    POST /sync - Upload 6 CSV files and trigger full workflow.
    
    This endpoint accepts multipart/form-data with 6 CSV files, triggers the
    complete LangGraph workflow (all 5 agents), and returns a summary of results.
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
        
        # Execute workflow — pass flask_app and db so results get persisted to SQLite
        result = await execute_workflow(csv_files, flask_app=flask_app, db=db)
        
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


def _safe_float(val, default=0.0):
    """Safely convert a SQLAlchemy Numeric/Decimal to float."""
    if val is None:
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _build_top_drivers(pred):
    """Build a top-drivers list from a RiskPrediction row."""
    drivers = []
    for i in range(1, 4):
        feat = getattr(pred, f'top_driver_{i}', None)
        contrib = _safe_float(getattr(pred, f'top_driver_{i}_contribution', None))
        if feat:
            drivers.append({
                "feature": feat,
                "contribution": contrib,
                "direction": "positive" if contrib > 0 else "negative"
            })
    return drivers


def _fetch_vendor_risks_from_neo4j(user_role: str, user_gstin: str | None):
    """
    Query Neo4j for vendor/counterparty risk data.

    For Business_Owner: find all counterparty taxpayers connected via invoices.
    For Admin: find top high-risk vendors across the graph.
    Returns list of vendor risk dicts.
    """
    vendor_risks = []
    try:
        from neo4j import GraphDatabase

        neo4j_uri = os.environ.get('NEO4J_URI')
        neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
        neo4j_password = os.environ.get('NEO4J_PASSWORD')

        if not neo4j_uri or not neo4j_password:
            return vendor_risks

        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

        with driver.session() as session:
            if user_role == 'Admin':
                query = """
                MATCH (t:Taxpayer)
                WHERE t.risk_level IN ['HIGH_RISK', 'MEDIUM_RISK']
                RETURN t.gstin AS vendor_gstin,
                       COALESCE(t.business_name, t.gstin) AS vendor_name,
                       COALESCE(t.risk_level, 'UNKNOWN') AS risk_level,
                       COALESCE(t.risk_probability, 0) AS risk_probability,
                       t.last_transaction_date AS last_transaction_date
                ORDER BY t.risk_probability DESC
                LIMIT 20
                """
                result = session.run(query)
            else:
                query = """
                MATCH (me:Taxpayer {gstin: $gstin})-[:ISSUED]->(i:Invoice)-[:TO]->(vendor:Taxpayer)
                RETURN vendor.gstin AS vendor_gstin,
                       COALESCE(vendor.business_name, vendor.gstin) AS vendor_name,
                       COALESCE(vendor.risk_level, 'UNKNOWN') AS risk_level,
                       COALESCE(vendor.risk_probability, 0) AS risk_probability,
                       vendor.last_transaction_date AS last_transaction_date
                UNION
                MATCH (supplier:Taxpayer)-[:ISSUED]->(i:Invoice)-[:TO]->(me:Taxpayer {gstin: $gstin})
                RETURN supplier.gstin AS vendor_gstin,
                       COALESCE(supplier.business_name, supplier.gstin) AS vendor_name,
                       COALESCE(supplier.risk_level, 'UNKNOWN') AS risk_level,
                       COALESCE(supplier.risk_probability, 0) AS risk_probability,
                       supplier.last_transaction_date AS last_transaction_date
                """
                result = session.run(query, gstin=user_gstin)

            for record in result:
                vendor_risks.append({
                    "vendor_gstin": record["vendor_gstin"],
                    "vendor_name": record["vendor_name"] or record["vendor_gstin"],
                    "risk_level": record["risk_level"],
                    "itc_at_risk": round(float(record.get("risk_probability", 0) or 0) * 100000, 2),
                    "last_transaction_date": record.get("last_transaction_date") or "N/A",
                })

        driver.close()

    except Exception as e:
        logger.warning(f"Could not fetch vendor risks from Neo4j: {str(e)}")

    return vendor_risks


@app.get("/dashboard")
async def get_dashboard(current_user: User = Depends(get_current_user)):
    """
    GET /dashboard – Retrieve dashboard data with RBAC filtering.

    Admin  → aggregated system-wide view (total taxpayers, risk distribution,
             fraud pattern entity details, vendor risks from Neo4j).
    Business_Owner → single-entity view (own GSTIN risk, health, vendors).
    """
    try:
        with flask_app.app_context():
            from models import RiskPrediction, FraudPattern, EngineeredFeatures

            # ── RBAC-filtered risk predictions ──────────────────────────
            if current_user.role == 'Admin':
                risk_predictions = RiskPrediction.query.all()
            else:
                risk_predictions = RiskPrediction.query.filter_by(
                    gstin=current_user.gstin
                ).all()

            # ── Fraud patterns ──────────────────────────────────────────
            if current_user.role == 'Admin':
                patterns = FraudPattern.query.all()
            else:
                patterns = FraudPattern.query.all()
                # Filter to patterns involving this GSTIN
                patterns = [
                    p for p in patterns
                    if current_user.gstin in (p.gstin_list or [])
                ]

            # ── Build pattern entity detail lists ───────────────────────
            circular_entities = []
            ghost_entities = []
            spider_entities = []

            for p in patterns:
                gstins = p.gstin_list or []
                if p.pattern_type == 'circular_trade':
                    for idx, g in enumerate(gstins):
                        partner = gstins[(idx + 1) % len(gstins)] if len(gstins) > 1 else 'N/A'
                        circular_entities.append({
                            "gstin": g,
                            "partner_gstin": partner,
                            "pattern": "circular_trade",
                        })
                elif p.pattern_type == 'ghost_invoice':
                    meta = p.pattern_metadata or {}
                    for g in gstins:
                        ghost_entities.append({
                            "gstin": g,
                            "ghost_invoice_count": meta.get("ghost_count", 0),
                            "pattern": "ghost_invoice",
                        })
                elif p.pattern_type == 'spider_web':
                    meta = p.pattern_metadata or {}
                    for g in gstins:
                        spider_entities.append({
                            "gstin": g,
                            "shared_contact_count": meta.get("spoke_count",
                                                              meta.get("cluster_size", 0)),
                            "pattern": "spider_web",
                        })

            patterns_summary = {
                "circular_trade": len([p for p in patterns if p.pattern_type == 'circular_trade']),
                "ghost_invoices": len([p for p in patterns if p.pattern_type == 'ghost_invoice']),
                "spider_web_involvement": any(p.pattern_type == 'spider_web' for p in patterns),
                "circular_entities": circular_entities,
                "ghost_entities": ghost_entities,
                "spider_entities": spider_entities,
            }

            # ── Vendor risks from Neo4j ─────────────────────────────────
            vendor_risks = _fetch_vendor_risks_from_neo4j(
                current_user.role, current_user.gstin
            )

            # ── Empty-data handling (return zeros, not 404) ─────────────
            if not risk_predictions:
                return {
                    "gstin": current_user.gstin,
                    "health_score": 100.0,
                    "risk_level": "LOW_RISK",
                    "risk_probability": 0.0,
                    "top_drivers": [],
                    "total_taxpayers": 0,
                    "high_risk_count": 0,
                    "medium_risk_count": 0,
                    "low_risk_count": 0,
                    "vendor_risks": vendor_risks,
                    "patterns": patterns_summary,
                    "data_source": "no_data",
                }

            # ── Aggregated metrics (Admin) or single-entity ─────────────
            total = len(risk_predictions)
            high = sum(1 for p in risk_predictions if p.risk_level == 'HIGH_RISK')
            medium = sum(1 for p in risk_predictions if p.risk_level == 'MEDIUM_RISK')
            low = total - high - medium

            primary_pred = risk_predictions[0]
            top_drivers = _build_top_drivers(primary_pred)

            if current_user.role == 'Admin':
                # Average health score across all entities
                avg_prob = sum(_safe_float(p.risk_probability) for p in risk_predictions) / max(total, 1)
                health_score = round(100 - avg_prob * 100, 2)
            else:
                health_score = round(100 - _safe_float(primary_pred.risk_probability) * 100, 2)

            return {
                "gstin": primary_pred.gstin,
                "health_score": health_score,
                "risk_level": primary_pred.risk_level,
                "risk_probability": _safe_float(primary_pred.risk_probability),
                "top_drivers": top_drivers,
                "total_taxpayers": total,
                "high_risk_count": high,
                "medium_risk_count": medium,
                "low_risk_count": low,
                "vendor_risks": vendor_risks,
                "patterns": patterns_summary,
                "data_source": "sqlite" if not vendor_risks else "hybrid",
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
                return {
                    "gstin": gstin,
                    "risk_level": "UNKNOWN",
                    "risk_probability": 0.0,
                    "top_drivers": [],
                    "shape_plots": [],
                    "data_source": "no_data"
                }
            
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
            
            # Get audit narrative
            from models import AuditNarrative
            audit_narrative = AuditNarrative.query.filter_by(gstin=gstin).order_by(AuditNarrative.generated_at.desc()).first()
            narrative_text = audit_narrative.narrative_text if audit_narrative else "No detailed audit narrative available for this vendor."

            return {
                "gstin": gstin,
                "risk_level": risk_pred.risk_level,
                "risk_probability": float(risk_pred.risk_probability),
                "narrative": narrative_text,
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


# ============================================================================
# LIVE INJECTION: POST /api/v1/live-file
# ============================================================================

@app.post("/api/v1/live-file")
async def process_live_filing(
    payload: LiveFileRequest
):
    """
    POST /api/v1/live-file — Simulate a government portal filing.

    1. Injects the invoice into Neo4j (MERGE taxpayers, CREATE invoice)
    2. Runs cycle detection to check for circular trading
    3. Computes a heuristic EBM risk score on the new transaction
    4. Persists the invoice to SQLite
    5. Returns full result for frontend to animate
    """
    import random
    import hashlib

    doc_no = f"INV-LIVE-{int(datetime.now().timestamp())}"
    irn = hashlib.sha256(doc_no.encode()).hexdigest()[:32]
    timestamp = datetime.now().isoformat()

    is_circular = False
    cycle_path: list = []
    neo4j_injected = False

    # ── 1. Inject into Neo4j ────────────────────────────────────────────
    try:
        from neo4j import GraphDatabase

        neo4j_uri = os.environ.get('NEO4J_URI')
        neo4j_user_env = os.environ.get('NEO4J_USER', 'neo4j')
        neo4j_password = os.environ.get('NEO4J_PASSWORD')

        if neo4j_uri and neo4j_password:
            driver = GraphDatabase.driver(
                neo4j_uri, auth=(neo4j_user_env, neo4j_password)
            )

            with driver.session() as session:
                # MERGE taxpayer nodes, CREATE invoice node & relationships
                inject_query = """
                MERGE (s:Taxpayer {gstin: $seller})
                  ON CREATE SET s.business_name = $seller, s.risk_level = 'UNKNOWN'
                MERGE (b:Taxpayer {gstin: $buyer})
                  ON CREATE SET b.business_name = $buyer, b.risk_level = 'UNKNOWN'
                CREATE (i:Invoice {
                    irn: $irn, doc_no: $doc_no,
                    amt: $amt, tax: $tax,
                    hsn: $hsn, timestamp: datetime()
                })
                MERGE (s)-[:ISSUED]->(i)
                MERGE (i)-[:TO]->(b)
                RETURN i.irn AS irn
                """
                session.run(
                    inject_query,
                    seller=payload.seller_gstin,
                    buyer=payload.buyer_gstin,
                    irn=irn,
                    doc_no=doc_no,
                    amt=payload.amount,
                    tax=payload.tax,
                    hsn=payload.hsn_code or '',
                )
                neo4j_injected = True

                # ── 2. Cycle detection ──────────────────────────────────
                cycle_query = """
                MATCH p=(s:Taxpayer {gstin: $seller})
                      -[:ISSUED|TO*3..8]->
                      (s)
                WITH p LIMIT 1
                RETURN [n IN nodes(p) | CASE
                    WHEN n:Taxpayer THEN n.gstin
                    WHEN n:Invoice  THEN n.doc_no
                    ELSE toString(id(n))
                END] AS cycle_path
                """
                cycle_result = session.run(
                    cycle_query, seller=payload.seller_gstin
                )
                for record in cycle_result:
                    is_circular = True
                    cycle_path = record['cycle_path']
                    break

            driver.close()

    except Exception as e:
        logger.warning(f"Neo4j live injection warning: {str(e)}")

    # ── 3. Heuristic EBM risk scoring ───────────────────────────────────
    #    Simulates an Explainable Boosting Machine local explanation.
    #    Uses the invoice attributes to produce a realistic risk vector.

    base_risk = 0.15  # baseline risk for any new transaction

    # Driver 1 — Payment gap anomaly (high amounts are riskier)
    amount_factor = min(payload.amount / 500000, 1.0)  # normalize to 5L
    payment_gap_contrib = round(amount_factor * 0.30, 4)

    # Driver 2 — Self-dealing / related-party flag
    self_deal_contrib = 0.0
    if payload.seller_gstin[:2] == payload.buyer_gstin[:2]:
        self_deal_contrib = 0.12  # same-state trade slightly riskier
    if payload.seller_gstin == payload.buyer_gstin:
        self_deal_contrib = 0.45  # self-invoicing — very suspicious

    # Driver 3 — Circular trade amplifier
    circular_contrib = 0.35 if is_circular else 0.0

    # Driver 4 — Tax ratio anomaly
    expected_tax_ratio = 0.18  # 18% GST
    actual_tax_ratio = payload.tax / max(payload.amount, 1)
    tax_anomaly_contrib = round(abs(actual_tax_ratio - expected_tax_ratio) * 0.8, 4)

    risk_score = min(
        base_risk + payment_gap_contrib + self_deal_contrib
        + circular_contrib + tax_anomaly_contrib,
        0.99
    )
    risk_score = round(risk_score, 4)

    if risk_score >= 0.7:
        risk_level = 'HIGH_RISK'
    elif risk_score >= 0.4:
        risk_level = 'MEDIUM_RISK'
    else:
        risk_level = 'LOW_RISK'

    top_drivers = [
        {"feature": "payment_gap_anomaly", "contribution": payment_gap_contrib,
         "direction": "positive"},
        {"feature": "circular_trade_flag", "contribution": circular_contrib,
         "direction": "positive" if circular_contrib > 0 else "neutral"},
        {"feature": "tax_ratio_anomaly", "contribution": tax_anomaly_contrib,
         "direction": "positive"},
    ]
    if self_deal_contrib > 0:
        top_drivers.insert(1, {
            "feature": "self_dealing_flag", "contribution": self_deal_contrib,
            "direction": "positive"
        })
    top_drivers.sort(key=lambda d: d['contribution'], reverse=True)
    top_drivers = top_drivers[:3]

    # ── 4. Generate audit trail message ─────────────────────────────────
    if is_circular:
        audit_trail = (
            f"⚠️ CIRCULAR TRADE DETECTED. This filing from {payload.seller_gstin} "
            f"to {payload.buyer_gstin} completes a transaction loop: "
            f"{' → '.join(cycle_path[:6])}. "
            f"EBM risk score: {risk_score:.0%}. Flagged for immediate review."
        )
    elif risk_level == 'HIGH_RISK':
        audit_trail = (
            f"Filing processed but flagged HIGH RISK (score: {risk_score:.0%}). "
            f"Top driver: {top_drivers[0]['feature']} "
            f"(contribution: {top_drivers[0]['contribution']:.2f}). "
            f"Manual audit recommended."
        )
    elif risk_level == 'MEDIUM_RISK':
        audit_trail = (
            f"Filing processed. Medium risk detected (score: {risk_score:.0%}). "
            f"Monitoring anomaly in {top_drivers[0]['feature']}."
        )
    else:
        audit_trail = (
            f"Filing processed successfully. Low risk (score: {risk_score:.0%}). "
            f"No anomalies detected."
        )

    # ── 5. Persist to SQLite ────────────────────────────────────────────
    try:
        with flask_app.app_context():
            from models import RawInvoice
            from datetime import date

            new_invoice = RawInvoice(
                irn=irn,
                seller_gstin=payload.seller_gstin,
                buyer_gstin=payload.buyer_gstin,
                invoice_value=payload.amount + payload.tax,
                invoice_date=date.today(),
                doc_no=doc_no,
            )
            db.session.add(new_invoice)
            db.session.commit()
    except Exception as e:
        logger.warning(f"SQLite persist warning for live filing: {str(e)}")

    logger.info(
        f"Live filing: {doc_no} | {payload.seller_gstin} → {payload.buyer_gstin} "
        f"| ₹{payload.amount:,.2f} | risk={risk_score:.2%} | circular={is_circular}"
    )

    return {
        "status": "success",
        "new_invoice_id": doc_no,
        "irn": irn,
        "seller_gstin": payload.seller_gstin,
        "buyer_gstin": payload.buyer_gstin,
        "amount": payload.amount,
        "tax": payload.tax,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "is_circular": is_circular,
        "cycle_path": cycle_path,
        "audit_trail": audit_trail,
        "top_drivers": top_drivers,
        "neo4j_injected": neo4j_injected,
        "timestamp": timestamp,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

