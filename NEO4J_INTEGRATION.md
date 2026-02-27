# Neo4j Integration - Complete Guide

## Overview

The system now fetches data from Neo4j database instead of SQLite for graph visualization and admin dashboard. This enables handling of large datasets (2000+ entities, 15000+ relationships).

## Changes Implemented

### 1. Graph Endpoint (`/graph`)

**File**: `backend/app.py`

The `/graph` endpoint now:
- ✅ Fetches data from Neo4j first
- ✅ Falls back to SQLite if Neo4j fails
- ✅ Supports RBAC (Admin sees all, Business Owner sees their subgraph)
- ✅ Handles up to 2000 nodes and 15000 edges for admins
- ✅ Returns 2-hop neighborhood for business owners

**Admin Query** (All Data):
```cypher
// Nodes
MATCH (n)
WHERE n:Taxpayer OR n:Invoice OR n:EwayBill
RETURN ... 
LIMIT 2000

// Edges
MATCH (source)-[r]->(target)
WHERE (source:Taxpayer OR source:Invoice OR source:EwayBill)
  AND (target:Taxpayer OR target:Invoice OR target:EwayBill)
RETURN ...
LIMIT 15000
```

**Business Owner Query** (Subgraph):
```cypher
// Nodes (2-hop neighborhood)
MATCH path = (start:Taxpayer {gstin: $gstin})-[*0..2]-(connected)
WHERE connected:Taxpayer OR connected:Invoice OR connected:EwayBill
WITH DISTINCT connected as n
RETURN ...
LIMIT 500

// Edges (within subgraph)
MATCH path = (start:Taxpayer {gstin: $gstin})-[*0..2]-(connected)
WITH DISTINCT connected
MATCH (source)-[r]->(target)
WHERE (source = connected OR target = connected)
RETURN ...
LIMIT 2000
```

### 2. Admin Dashboard Endpoint (`/dashboard`)

**File**: `backend/app.py`

The admin dashboard now:
- ✅ Fetches taxpayer data from Neo4j
- ✅ Gets risk levels and fraud patterns from Neo4j
- ✅ Falls back to SQLite if Neo4j fails
- ✅ Returns up to 2000 taxpayers

**Query**:
```cypher
MATCH (t:Taxpayer)
RETURN 
    t.gstin as gstin,
    t.business_name as business_name,
    t.risk_level as risk_level,
    t.risk_probability as risk_probability,
    t.in_circular_trade as in_circular_trade,
    t.last_transaction_date as last_transaction_date
LIMIT 2000
```

### 3. Frontend Updates

**File**: `frontend/src/app/graph/page.tsx`

- ✅ Added console logging to show data source (neo4j/sqlite)
- ✅ Displays node and edge counts
- ✅ Better error handling

## Neo4j Configuration

### Environment Variables

**File**: `backend/.env`

```env
NEO4J_URI=neo4j+s://4d1f78fe.databases.neo4j.io
NEO4J_USER=4d1f78fe
NEO4J_PASSWORD=dcioMSh9pXOEG0mq30_YhVic_i2L5ijsVf4hKlYge3Y
```

### Connection Manager

**File**: `backend/utils/db_connection.py`

```python
class Neo4jConnection:
    """Neo4j connection manager using official driver."""
    
    def connect(self):
        """Establish connection to Neo4j."""
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )
        return self
    
    def execute_query(self, query, parameters=None):
        """Execute a Cypher query and return results."""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
```

## Data Model in Neo4j

### Node Types

1. **Taxpayer**
   ```
   Properties:
   - gstin: string (unique identifier)
   - business_name: string
   - risk_level: string (HIGH_RISK, MEDIUM_RISK, LOW_RISK)
   - risk_probability: float
   - in_circular_trade: boolean
   - last_transaction_date: date
   ```

2. **Invoice**
   ```
   Properties:
   - irn: string (unique identifier)
   - doc_no: string
   - invoice_value: float
   - invoice_date: date
   ```

3. **EwayBill**
   ```
   Properties:
   - doc_no: string (unique identifier)
   - vehicle_no: string
   - distance: integer
   - generated_date: date
   ```

### Relationship Types

1. **ISSUED** - Taxpayer → Invoice
2. **TO** - Invoice → Taxpayer
3. **BACKED_BY** - Invoice → EwayBill
4. **CIRCULAR_TRADE** - Taxpayer → Taxpayer
5. **SHARED_CONTACT** - Taxpayer → Taxpayer

## API Response Format

### GET /graph

**Success Response**:
```json
{
  "nodes": [
    {
      "id": "29AABCT1332L1Z5",
      "label": "Taxpayer",
      "name": "ABC Corp Ltd",
      "risk_level": "HIGH_RISK",
      "in_circular_trade": true
    },
    {
      "id": "IRN123456",
      "label": "Invoice",
      "name": "IRN123456",
      "value": 250000.00,
      "date": "2026-01-15"
    }
  ],
  "edges": [
    {
      "source": "29AABCT1332L1Z5",
      "target": "IRN123456",
      "type": "ISSUED"
    }
  ],
  "count": {
    "nodes": 2000,
    "edges": 15000
  },
  "source": "neo4j"
}
```

### GET /dashboard (Admin)

**Success Response**:
```json
{
  "health_score": 75.5,
  "total_taxpayers": 2000,
  "high_risk_count": 150,
  "medium_risk_count": 600,
  "low_risk_count": 1250,
  "vendor_risks": [
    {
      "vendor_gstin": "29AABCT1332L1Z5",
      "vendor_name": "ABC Corp Ltd",
      "risk_level": "HIGH_RISK",
      "itc_at_risk": 0,
      "last_transaction_date": "2026-02-28"
    }
  ],
  "patterns": {
    "circular_trade": 45,
    "ghost_invoices": 0,
    "spider_web_involvement": true
  },
  "is_admin": true,
  "data_source": "neo4j"
}
```

## Fallback Mechanism

### When Neo4j Fails

The system automatically falls back to SQLite:

1. **Connection Failure**: If Neo4j connection cannot be established
2. **Query Failure**: If Cypher query fails
3. **No Data**: If Neo4j returns empty results

**Fallback Functions**:
- `graph_from_sqlite(current_user)` - For graph endpoint
- `admin_dashboard_from_sqlite()` - For admin dashboard

### Fallback Indicators

- Response includes `"source": "sqlite"` instead of `"source": "neo4j"`
- Console logs show fallback messages
- Smaller dataset (limited to SQLite data)

## Performance Considerations

### Query Limits

- **Admin Graph**: 2000 nodes, 15000 edges
- **Business Owner Graph**: 500 nodes, 2000 edges
- **Admin Dashboard**: 2000 taxpayers

### Optimization Tips

1. **Indexes**: Ensure Neo4j has indexes on:
   - `Taxpayer.gstin`
   - `Invoice.irn`
   - `EwayBill.doc_no`

2. **Constraints**: Create uniqueness constraints:
   ```cypher
   CREATE CONSTRAINT taxpayer_gstin IF NOT EXISTS
   FOR (t:Taxpayer) REQUIRE t.gstin IS UNIQUE;
   
   CREATE CONSTRAINT invoice_irn IF NOT EXISTS
   FOR (i:Invoice) REQUIRE i.irn IS UNIQUE;
   ```

3. **Connection Pooling**: Neo4j driver handles connection pooling automatically

4. **Batch Operations**: Use UNWIND for bulk inserts (see `utils/neo4j_batching.py`)

## Testing

### 1. Test Neo4j Connection

```bash
cd backend
python verify_setup.py
```

Look for:
```
==================================================
TESTING NEO4J CONNECTION
==================================================
✅ Neo4j connection successful
   Version: 5.x.x
```

### 2. Test Graph Endpoint

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://127.0.0.1:5000/graph
```

Check response for:
- `"source": "neo4j"` (success) or `"source": "sqlite"` (fallback)
- `"count": {"nodes": X, "edges": Y}`

### 3. Test Admin Dashboard

```bash
curl -H "Authorization: Bearer ADMIN_TOKEN" \
     http://127.0.0.1:5000/dashboard
```

Check response for:
- `"data_source": "neo4j"` (success) or `"data_source": "sqlite"` (fallback)
- `"total_taxpayers": X`

### 4. Test Frontend

1. Login as admin: `admin@gstn.gov.in` / `admin123`
2. Navigate to `/graph`
3. Open browser console (F12)
4. Look for log: `Graph data loaded: X nodes, Y edges from neo4j`

## Troubleshooting

### Issue: "Neo4j connection failed"

**Causes**:
1. Neo4j server not running
2. Wrong credentials in `.env`
3. Network connectivity issues
4. Firewall blocking connection

**Solutions**:
1. Check Neo4j AuraDB status
2. Verify credentials in `.env`
3. Test connection: `python verify_setup.py`
4. Check firewall settings

### Issue: Graph shows "No data available"

**Causes**:
1. Neo4j database is empty
2. Query returned no results
3. RBAC filtering too restrictive

**Solutions**:
1. Populate Neo4j with data
2. Check Cypher queries in backend logs
3. Verify user has access to data

### Issue: Fallback to SQLite

**Causes**:
1. Neo4j query failed
2. Neo4j returned empty results
3. Connection timeout

**Solutions**:
1. Check backend logs for error messages
2. Verify Neo4j has data
3. Increase query timeout
4. Check network latency

### Issue: Graph loads slowly

**Causes**:
1. Large dataset (>2000 nodes)
2. Complex queries
3. Network latency
4. No indexes on Neo4j

**Solutions**:
1. Reduce LIMIT in queries
2. Add indexes to Neo4j
3. Use pagination (future enhancement)
4. Optimize Cypher queries

## Data Population

### Option 1: Use Ingestion Pipeline

```bash
cd backend
python -c "from orchestration.llm_agent import execute_workflow_sync; execute_workflow_sync('Ingest data from CSV files')"
```

### Option 2: Manual Cypher Queries

```cypher
// Create Taxpayer
CREATE (t:Taxpayer {
  gstin: '29AABCT1332L1Z5',
  business_name: 'ABC Corp Ltd',
  risk_level: 'HIGH_RISK',
  risk_probability: 0.785,
  in_circular_trade: true,
  last_transaction_date: date('2026-02-28')
})

// Create Invoice
CREATE (i:Invoice {
  irn: 'IRN123456',
  doc_no: 'INV001',
  invoice_value: 250000.00,
  invoice_date: date('2026-01-15')
})

// Create Relationship
MATCH (t:Taxpayer {gstin: '29AABCT1332L1Z5'})
MATCH (i:Invoice {irn: 'IRN123456'})
CREATE (t)-[:ISSUED]->(i)
```

### Option 3: Bulk Import from CSV

```cypher
// Load Taxpayers
LOAD CSV WITH HEADERS FROM 'file:///entity_master.csv' AS row
CREATE (t:Taxpayer {
  gstin: row.gstin,
  business_name: row.business_name,
  risk_level: row.risk_level,
  risk_probability: toFloat(row.risk_probability)
})

// Load Invoices
LOAD CSV WITH HEADERS FROM 'file:///e_invoices.csv' AS row
CREATE (i:Invoice {
  irn: row.irn,
  doc_no: row.doc_no,
  invoice_value: toFloat(row.invoice_value),
  invoice_date: date(row.invoice_date)
})
```

## Monitoring

### Backend Logs

Check for:
```
Graph data loaded: 2000 nodes, 15000 edges from neo4j
Neo4j query failed, falling back to SQLite: [error message]
```

### Frontend Console

Check for:
```
Graph data loaded: 2000 nodes, 15000 edges from neo4j
```

### Neo4j Browser

Access: https://4d1f78fe.databases.neo4j.io/browser/

Run queries:
```cypher
// Count nodes
MATCH (n) RETURN labels(n) as label, count(n) as count

// Count relationships
MATCH ()-[r]->() RETURN type(r) as type, count(r) as count

// Check data
MATCH (t:Taxpayer) RETURN t LIMIT 10
```

## Future Enhancements

1. **Pagination**: Load data in chunks for better performance
2. **Caching**: Cache frequently accessed subgraphs
3. **Real-time Updates**: WebSocket for live graph updates
4. **Advanced Queries**: Support for custom Cypher queries
5. **Graph Analytics**: Centrality, community detection, path finding
6. **Export**: Download graph data as JSON/CSV
7. **Filters**: Filter by risk level, date range, entity type
8. **Search**: Search for specific entities in graph

## Status

✅ **FULLY FUNCTIONAL**

The system now fetches data from Neo4j for:
- Graph visualization (up to 2000 nodes, 15000 edges)
- Admin dashboard (up to 2000 taxpayers)
- With automatic fallback to SQLite if Neo4j fails

**Last Updated**: February 28, 2026
**Version**: 3.0.0 (Neo4j Integration)
