from database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Must be 'Admin' or 'Business_Owner'
    gstin = db.Column(db.String(15), nullable=True)  # GSTIN for Business_Owner role
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email}>"


class RawInvoice(db.Model):
    __tablename__ = 'raw_invoices'
    id = db.Column(db.Integer, primary_key=True)
    irn = db.Column(db.String(64), unique=True, nullable=False)
    seller_gstin = db.Column(db.String(15), nullable=False)
    buyer_gstin = db.Column(db.String(15), nullable=False)
    invoice_value = db.Column(db.Numeric(15, 2), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    doc_no = db.Column(db.String(50), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RawInvoice {self.irn}>"


class RawEwayBill(db.Model):
    __tablename__ = 'raw_eway_bills'
    id = db.Column(db.Integer, primary_key=True)
    doc_no = db.Column(db.String(50), nullable=False)
    vehicle_no = db.Column(db.String(20))
    distance = db.Column(db.Integer)
    generated_date = db.Column(db.Date, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RawEwayBill {self.doc_no}>"


class EntityMaster(db.Model):
    __tablename__ = 'entity_master'
    id = db.Column(db.Integer, primary_key=True)
    gstin = db.Column(db.String(15), unique=True, nullable=False)
    business_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(255))
    address = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<EntityMaster {self.gstin}>"


class EngineeredFeatures(db.Model):
    __tablename__ = 'engineered_features'
    id = db.Column(db.Integer, primary_key=True)
    gstin = db.Column(db.String(15), nullable=False)
    payment_gap = db.Column(db.Numeric(10, 2))
    payment_gap_pct = db.Column(db.Numeric(10, 4))
    ghost_invoice_pct = db.Column(db.Numeric(10, 4))
    shared_contact_flag = db.Column(db.Boolean)
    filing_gap = db.Column(db.Numeric(15, 2))
    excess_itc_flag = db.Column(db.Boolean)
    avg_invoice_value = db.Column(db.Numeric(15, 2))
    transaction_count = db.Column(db.Integer)
    filing_delay_avg = db.Column(db.Numeric(10, 2))
    circular_trade_involvement = db.Column(db.Integer)
    spider_web_involvement = db.Column(db.Integer)
    vendor_diversity = db.Column(db.Numeric(10, 4))
    buyer_concentration = db.Column(db.Numeric(10, 4))
    seasonal_anomaly_score = db.Column(db.Numeric(10, 4))
    computed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<EngineeredFeatures {self.gstin}>"


class RiskPrediction(db.Model):
    __tablename__ = 'risk_predictions'
    id = db.Column(db.Integer, primary_key=True)
    gstin = db.Column(db.String(15), nullable=False)
    risk_probability = db.Column(db.Numeric(5, 4), nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    top_driver_1 = db.Column(db.String(100))
    top_driver_1_contribution = db.Column(db.Numeric(10, 4))
    top_driver_2 = db.Column(db.String(100))
    top_driver_2_contribution = db.Column(db.Numeric(10, 4))
    top_driver_3 = db.Column(db.String(100))
    top_driver_3_contribution = db.Column(db.Numeric(10, 4))
    model_version = db.Column(db.String(50))
    predicted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RiskPrediction {self.gstin} - {self.risk_level}>"


class FraudPattern(db.Model):
    __tablename__ = 'fraud_patterns'
    id = db.Column(db.Integer, primary_key=True)
    pattern_type = db.Column(db.String(50), nullable=False)
    # Use JSON for SQLite compatibility, ARRAY for PostgreSQL
    gstin_list = db.Column(db.JSON, nullable=False)
    risk_score = db.Column(db.Numeric(5, 4))
    pattern_metadata = db.Column(db.JSON)
    detection_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FraudPattern {self.pattern_type}>"


class AuditNarrative(db.Model):
    __tablename__ = 'audit_narratives'
    id = db.Column(db.Integer, primary_key=True)
    gstin = db.Column(db.String(15), nullable=False)
    narrative_text = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditNarrative {self.gstin}>"


class ShapePlot(db.Model):
    __tablename__ = 'shape_plots'
    id = db.Column(db.Integer, primary_key=True)
    gstin = db.Column(db.String(15), nullable=False)
    feature_name = db.Column(db.String(100), nullable=False)
    contribution_weight = db.Column(db.Numeric(10, 4), nullable=False)
    feature_value = db.Column(db.Numeric(15, 4), nullable=False)
    baseline_value = db.Column(db.Numeric(15, 4), nullable=False)
    x_values = db.Column(db.JSON)  # Array of x-axis values for shape plot
    y_values = db.Column(db.JSON)  # Array of y-axis values for shape plot
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ShapePlot {self.gstin} - {self.feature_name}>"
