# Upload and Data Processing Pipeline

## Overview

The upload facility allows business owners to submit GST transaction data for fraud detection analysis. The system processes 6 CSV files through a multi-agent AI pipeline to detect fraud patterns.

## Upload Process

### 1. Frontend Upload (`/upload` page)

**Required Files** (all CSV format):
1. **E-Invoices** (`e_invoices.csv`) - Electronic invoices issued
2. **E-Way Bills** (`eway_bills.csv`) - Goods movement documents
3. **Entity Master** (`entity_master.csv`) - Business entity information
4. **Filing History** (`filing_history.csv`) - Tax filing records
5. **Purchase Register** (`purchase_register.csv`) - Purchase transactions
6. **Returns Summary** (`returns_summary.csv`) - GST return summaries

**Upload Flow**:
```
User selects 6 CSV files → Validates all files present → Sends to `/sync` endpoint → Shows progress → Displays results
```

### 2. Backend Endpoint (`/sync`)

**Current Status**: ⚠️ **NOT IMPLEMENTED in Flask backend**

The Flask backend (`backend/app.py`) does NOT have a `/sync` endpoint. This endpoint only exists in the FastAPI backend (`backend/app_fastapi.py`).

**To use upload functionality**: You must switch to FastAPI backend:
```bash
cd backend
uvicorn app_fastapi:app --reload --port 5000
```

## Data Processing Pipeline (FastAPI Backend)

When files are uploaded to FastAPI's `/sync` endpoint, they go through a **5-agent workflow**:

### Agent 1: Ingestion Wrangler
**File**: `backend/orchestration/agent_ingestion_wrangler.py`

**Purpose**: Validate and clean CSV data

**Tasks**:
1. **Schema Validation**
   - Check required columns exist
   - Validate data types (dates, numbers, GSTINs)
   - Ensure no missing critical fields

2. **Data Cleaning**
   - Remove duplicates
   - Fix formatting issues
   - Standardize GSTIN format
   - Parse dates correctly

3. **Business Rule Validation**
   - GSTIN format: 15 characters, alphanumeric
   - Invoice amounts > 0
   - Dates in valid range
   - E-way bill numbers match invoices

**Output**: Clean, validated CSV data ready for processing

**Example Validation**:
```python
# Check GSTIN format
if not re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', gstin):
    raise ValidationError(f"Invalid GSTIN format: {gstin}")

# Check invoice amount
if invoice_amount <= 0:
    raise ValidationError(f"Invoice amount must be positive: {invoice_amount}")
```

### Agent 2: Graph Architect
**File**: `backend/orchestration/agent_graph_architect.py`

**Purpose**: Build Neo4j knowledge graph from CSV data

**Tasks**:
1. **Create Nodes**
   - Taxpayer nodes (from entity_master.csv)
   - Invoice nodes (from e_invoices.csv)
   - EwayBill nodes (from eway_bills.csv)

2. **Create Relationships**
   - `ISSUED`: Taxpayer → Invoice (who issued the invoice)
   - `TO`: Invoice → Taxpayer (who received the invoice)
   - `BACKED_BY`: Invoice → EwayBill (invoice has e-way bill)
   - `SHARED_CONTACT`: Taxpayer → Taxpayer (shared phone/email)

3. **Set Properties**
   - Taxpayer: GSTIN, business_name, sector, status, kyc_score
   - Invoice: IRN, doc_no, invoice_value, invoice_date
   - EwayBill: eway_bill_no, doc_no, vehicle_no

**Output**: Neo4j graph with 2000+ nodes and 15000+ relationships

**Example Cypher Queries**:
```cypher
// Create Taxpayer node
CREATE (t:Taxpayer {
    gstin: '27AAAAA7009A1Z0',
    business_name: 'ABC Corp',
    sector: 'Manufacturing',
    status: 'Active',
    kyc_score: 75
})

// Create relationship
MATCH (t1:Taxpayer {gstin: '27AAAAA7009A1Z0'})
MATCH (t2:Taxpayer {gstin: '27AAAAA5558A1Z1'})
CREATE (t1)-[:ISSUED]->(i:Invoice {irn: 'INV001', value: 100000})-[:TO]->(t2)
```

### Agent 3: Predictive Analyst
**File**: `backend/orchestration/agent_predictive_analyst.py`

**Purpose**: Calculate fraud risk scores using ML model

**Tasks**:
1. **Feature Engineering**
   - Extract features from graph (transaction count, partner diversity, etc.)
   - Calculate ratios (ITC/turnover, purchases/sales)
   - Identify anomalies (sudden spikes, dormant periods)

2. **Risk Scoring**
   - Use EBM (Explainable Boosting Machine) model
   - Calculate risk probability (0-1 scale)
   - Classify as HIGH/MEDIUM/LOW risk

3. **SHAP Analysis**
   - Identify top 3 risk drivers
   - Calculate feature contributions
   - Generate explanations

**Output**: Risk scores for all taxpayers

**Example Risk Calculation**:
```python
# Feature extraction
features = {
    'kyc_score': 45,  # Low KYC = higher risk
    'transaction_count': 0,  # No transactions = suspicious
    'unique_partners': 25,  # Too many partners = suspicious
    'itc_ratio': 0.95,  # High ITC ratio = suspicious
}

# ML model prediction
risk_probability = ebm_model.predict_proba(features)[0][1]  # 0.78 (78%)
risk_level = 'HIGH_RISK' if risk_probability > 0.65 else 'MEDIUM_RISK' if risk_probability > 0.35 else 'LOW_RISK'
```

### Agent 4: Risk Detective
**File**: `backend/orchestration/agent_risk_detective.py`

**Purpose**: Detect structural fraud patterns in the graph

**Tasks**:
1. **Circular Trade Detection**
   - Find cycles: A → B → C → A
   - Identify all entities in the cycle
   - Calculate cycle length and value

2. **Ghost Invoice Detection**
   - Find invoices without e-way bills
   - Check for fake transactions
   - Identify suspicious patterns

3. **Spider Web Detection**
   - Find entities with shared contacts
   - Identify shell company networks
   - Map fraud rings

**Output**: List of fraud patterns with involved entities

**Example Fraud Detection**:
```cypher
// Detect circular trade (3-hop cycle)
MATCH path = (t1:Taxpayer)-[:ISSUED]->(:Invoice)-[:TO]->(t2:Taxpayer)
             -[:ISSUED]->(:Invoice)-[:TO]->(t3:Taxpayer)
             -[:ISSUED]->(:Invoice)-[:TO]->(t1)
WHERE t1 <> t2 AND t2 <> t3 AND t3 <> t1
RETURN t1.gstin, t2.gstin, t3.gstin

// Detect ghost invoices
MATCH (i:Invoice)
WHERE NOT (i)-[:BACKED_BY]->(:EwayBill)
RETURN i.irn, i.invoice_value
```

### Agent 5: Niyati Explainer
**File**: `backend/orchestration/agent_niyati_explainer.py`

**Purpose**: Generate human-readable audit narratives

**Tasks**:
1. **Risk Summary**
   - Overall risk assessment
   - Key findings
   - Fraud involvement

2. **Detailed Analysis**
   - Transaction patterns
   - Partner analysis
   - Compliance issues

3. **Recommendations**
   - Immediate actions
   - Long-term improvements
   - Compliance steps

**Output**: Audit narrative for each taxpayer

**Example Narrative**:
```
Risk Assessment for GSTIN 27AAAAA7009A1Z0

RISK LEVEL: HIGH_RISK (78% probability)

KEY FINDINGS:
- Involved in 2 circular trade patterns
- 15 ghost invoices detected (₹25L total value)
- Shared contact with 8 other entities

FRAUD INDICATORS:
1. Circular Trade: Trading with 27AAAAA5558A1Z1 and 27AAAAA8421A1Z2 in a loop
2. Ghost Invoices: 15 invoices lack e-way bill backing
3. Spider Web: Part of a network of 8 entities sharing phone number

RECOMMENDATIONS:
- URGENT: Investigate circular trade patterns immediately
- WARNING: Provide e-way bills for all invoices
- ALERT: Verify independence of business partners
```

## Complete Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER UPLOADS 6 CSV FILES                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  AGENT 1: Ingestion Wrangler                                │
│  - Validate CSV schemas                                      │
│  - Clean and standardize data                                │
│  - Check business rules                                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  AGENT 2: Graph Architect                                    │
│  - Create Taxpayer, Invoice, EwayBill nodes                 │
│  - Build relationships (ISSUED, TO, BACKED_BY)              │
│  - Store in Neo4j graph database                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  AGENT 3: Predictive Analyst                                 │
│  - Extract features from graph                               │
│  - Run EBM ML model                                          │
│  - Calculate risk scores (0-1)                               │
│  - Classify as HIGH/MEDIUM/LOW                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  AGENT 4: Risk Detective                                     │
│  - Detect circular trade patterns                            │
│  - Find ghost invoices                                       │
│  - Identify spider web networks                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  AGENT 5: Niyati Explainer                                   │
│  - Generate audit narratives                                 │
│  - Create recommendations                                    │
│  - Produce human-readable reports                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    RESULTS DISPLAYED TO USER                 │
│  - Invoices processed: 15,005                                │
│  - Circular trade patterns: 133                              │
│  - Ghost invoices: 2,195                                     │
│  - Spider webs: 294                                          │
│  - High risk entities: 450                                   │
└─────────────────────────────────────────────────────────────┘
```

## Real-Time Progress Updates

The FastAPI backend uses **Server-Sent Events (SSE)** to stream progress updates:

```
[Agent 1] Starting data validation...
[Agent 1] Validated 15,005 invoices
[Agent 1] Validation complete ✓

[Agent 2] Building knowledge graph...
[Agent 2] Created 2,003 taxpayer nodes
[Agent 2] Created 15,005 invoice nodes
[Agent 2] Created 12,810 e-way bill nodes
[Agent 2] Graph construction complete ✓

[Agent 3] Calculating risk scores...
[Agent 3] Processed 500/2003 taxpayers
[Agent 3] Processed 1000/2003 taxpayers
[Agent 3] Risk scoring complete ✓

[Agent 4] Detecting fraud patterns...
[Agent 4] Found 133 circular trade patterns
[Agent 4] Found 2,195 ghost invoices
[Agent 4] Found 294 spider web networks
[Agent 4] Fraud detection complete ✓

[Agent 5] Generating audit narratives...
[Agent 5] Generated 2,003 narratives
[Agent 5] Analysis complete ✓

✅ Processing complete in 45.2 seconds
```

## Current Limitations (Flask Backend)

The Flask backend you're currently using does **NOT** have the upload functionality. It only:
- Computes risk scores on-the-fly from existing Neo4j data
- Does not process uploaded CSV files
- Does not run the agent workflow

## To Enable Upload Functionality

**Switch to FastAPI backend**:
```bash
# Stop Flask backend
# Start FastAPI backend
cd backend
uvicorn app_fastapi:app --reload --port 5000
```

Then the upload page will work and you'll see:
1. Real-time progress updates
2. Agent workflow execution
3. Fraud pattern detection
4. Complete analysis results

## Summary

**Upload Facility Purpose**:
- Allow business owners to submit GST transaction data
- Automatically detect fraud patterns
- Generate risk assessments
- Provide actionable recommendations

**Data Processing**:
- 5-agent AI pipeline
- Graph database construction
- ML-based risk scoring
- Pattern detection algorithms
- Human-readable narratives

**Current Status**:
- ⚠️ Flask backend: No upload functionality
- ✅ FastAPI backend: Full upload and processing pipeline
- 📊 Both backends: Real-time risk calculation from Neo4j
