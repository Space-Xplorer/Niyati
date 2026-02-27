# Project Niyati - Data Architecture

## Database Separation of Concerns

### SQLite (Primary Data Store)
**Purpose**: Store calculated risk predictions and fraud patterns from ML agents

**Contains**:
- `risk_predictions` - Risk scores calculated by EBM model
- `fraud_patterns` - Detected fraud patterns (circular trade, ghost invoices, spider webs)
- `entity_master` - Business entity information
- `audit_narratives` - Generated audit reports
- `users` - Authentication data

**Why SQLite?**
- Risk predictions are CALCULATED by ML agents (not graph data)
- Fraud patterns are DETECTED by analysis agents
- This is the source of truth for risk scores

### Neo4j (Graph Database)
**Purpose**: Store graph structure and relationships between entities

**Contains**:
- `Taxpayer` nodes - Basic entity information (GSTIN, sector, status, KYC score)
- `Invoice` nodes - Transaction documents
- `EwayBill` nodes - E-way bill documents
- Relationships - Connections between entities (ISSUED_TO, RECEIVED_FROM, etc.)

**Why Neo4j?**
- Graph visualization requires node/edge structure
- Relationship analysis (circular trade detection)
- Network pattern detection
- NOT for storing calculated risk scores

## Hybrid Approach for Admin Dashboard

The admin dashboard uses BOTH databases:

```
┌─────────────────────────────────────────────────────┐
│           Admin Dashboard Data Flow                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. Risk Predictions (SQLite)                       │
│     ├─ Total taxpayers                              │
│     ├─ High/Medium/Low risk counts                  │
│     ├─ Health scores                                │
│     ├─ Fraud pattern counts                         │
│     └─ Vendor risk table                            │
│                                                      │
│  2. Graph Statistics (Neo4j) - Optional             │
│     ├─ Total nodes in graph                         │
│     ├─ Total relationships                          │
│     └─ Network connectivity metrics                 │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Data Ingestion
```
CSV Files → SQLite (entity_master, invoices, etc.)
```

### 2. Graph Construction
```
SQLite → Neo4j (via agent_graph_architect.py)
- Creates Taxpayer, Invoice, EwayBill nodes
- Creates relationships between entities
```

### 3. Risk Calculation
```
SQLite → ML Agent (EBM model) → SQLite (risk_predictions)
- Reads entity data
- Calculates risk scores
- Stores predictions back to SQLite
```

### 4. Dashboard Display
```
SQLite (risk_predictions) + Neo4j (graph stats) → Frontend
- Primary data from SQLite
- Optional graph stats from Neo4j
```

## Why This Architecture?

### ❌ WRONG: Store risk predictions in Neo4j
- Risk scores are CALCULATED values, not graph properties
- Would require syncing between databases
- Neo4j is not optimized for analytical queries
- Adds complexity and potential inconsistency

### ✅ CORRECT: Hybrid approach
- SQLite: Source of truth for calculated risk data
- Neo4j: Source of truth for graph structure
- Each database does what it's best at
- No data duplication or sync issues

## API Endpoints

### `/dashboard` (Admin)
**Data Sources**:
- Primary: SQLite (risk_predictions, fraud_patterns)
- Optional: Neo4j (graph statistics)

**Returns**:
```json
{
  "health_score": 54.83,
  "total_taxpayers": 3,
  "high_risk_count": 1,
  "vendor_risks": [...],
  "patterns": {...},
  "neo4j_stats": {
    "taxpayers_in_graph": 2003,
    "relationships": 15000
  },
  "data_source": "hybrid"
}
```

### `/graph`
**Data Sources**:
- Primary: Neo4j (nodes, relationships)
- Fallback: SQLite (if Neo4j unavailable)

**Returns**:
```json
{
  "nodes": [...],
  "edges": [...],
  "source": "neo4j"
}
```

## Implementation Details

### Backend (`backend/app.py`)

```python
def admin_dashboard_data():
    # 1. Get risk predictions from SQLite (calculated by agents)
    all_predictions = RiskPrediction.query.all()
    
    # 2. Calculate metrics from risk predictions
    total_taxpayers = len(all_predictions)
    high_risk_count = len([p for p in all_predictions if p.risk_level == 'HIGH_RISK'])
    
    # 3. Optionally get Neo4j graph statistics
    try:
        neo4j_conn = get_neo4j_connection()
        stats = neo4j_conn.execute_query("MATCH (t:Taxpayer) RETURN count(t)")
        data_source = 'hybrid'
    except:
        data_source = 'sqlite'
    
    return {
        'health_score': ...,
        'total_taxpayers': total_taxpayers,
        'data_source': data_source
    }
```

### Frontend Display

The dashboard footer shows:
- `sqlite` - Risk data from SQLite only
- `hybrid` - Risk data from SQLite + graph stats from Neo4j

## Summary

✅ **SQLite**: Risk predictions calculated by ML agents (PRIMARY)
✅ **Neo4j**: Graph structure for visualization (SECONDARY)
✅ **Hybrid**: Best of both worlds - each DB does what it's best at
❌ **Don't**: Store calculated risk scores in Neo4j
❌ **Don't**: Try to sync data between databases

The admin dashboard now correctly shows risk data from SQLite (where it's calculated) with optional graph statistics from Neo4j.
