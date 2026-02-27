# Incremental Ingestion Setup

## Overview

Project Niyati now supports **incremental data ingestion**, meaning only new or updated records from CSV files are processed and pushed to Neo4j. This significantly improves performance when dealing with large datasets that change incrementally.

## How It Works

### 1. Change Detection

When CSV files are uploaded, the Ingestion Wrangler agent:

1. **Fetches existing data** from PostgreSQL tables
2. **Compares** new CSV data against existing records
3. **Identifies** three categories:
   - **New records**: Primary keys not in existing data
   - **Updated records**: Primary keys exist but content has changed
   - **Unchanged records**: Identical to existing data

4. **Computes hashes** for each record to detect content changes

### 2. Database Configuration

#### PostgreSQL Connection

The system uses the following environment variables (already configured in `.env`):

```env
PG_USER=postgres
PG_PASSWORD=Mahesh*456
PG_HOST=localhost
PG_PORT=5432
DB_NAME=postgres
DATABASE_URL=postgresql://postgres:Mahesh*456@localhost:5432/postgres
```

#### Neo4j Connection (AuraDB)

```env
NEO4J_URI=neo4j+s://4d1f78fe.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=dcioMSh9pXOEG0mq30_YhVic_i2L5ijsVf4hKlYge3Y
```

### 3. Change Detection Logic

For each CSV type, the system tracks:

| CSV Type | Primary Key | Content Columns |
|----------|-------------|-----------------|
| e_invoices | Irn | SellerGstin, BuyerGstin, DocNo, DocDt, TotalVal |
| eway_bills | DocNo | VehicleNo, Distance |
| entity_master | Gstin | Status, KycScore, SharedContact, Sector |
| filing_history | Gstin | Month, DelayDays |
| purchase_register | Irn | SellerGstin, BuyerGstin, DocNo, TotalVal |
| returns_summary | Gstin | Gstr1_Liability, Gstr3b_Paid |

### 4. Neo4j MERGE Operations

The Graph Architect agent (Task 4) will use **MERGE** instead of **CREATE** to handle updates:

```cypher
// Instead of CREATE
MERGE (t:Taxpayer {gstin: $gstin})
ON CREATE SET t.business_name = $business_name, t.status = $status
ON MATCH SET t.business_name = $business_name, t.status = $status
```

This ensures:
- New nodes are created if they don't exist
- Existing nodes are updated with new data
- No duplicate nodes are created

## Workflow

### First Upload (No Existing Data)

1. All CSV records are treated as **new**
2. All records are processed and pushed to Neo4j
3. Records are stored in PostgreSQL for future comparisons

### Subsequent Uploads (With Existing Data)

1. System fetches existing records from PostgreSQL
2. Change detection identifies:
   - 100 new invoices
   - 50 updated entities
   - 14,850 unchanged invoices
3. Only **new and updated** records are processed
4. Neo4j MERGE operations update the graph incrementally
5. PostgreSQL tables are updated with latest data

## State Management

The `NiyatiState` now includes a `change_summary` field:

```python
{
    'total_new': 150,
    'total_updated': 50,
    'total_unchanged': 14850,
    'details': {
        'e_invoices': {
            'new': DataFrame(...),
            'updated': DataFrame(...),
            'unchanged': DataFrame(...),
            'total_new': 100,
            'total_updated': 30,
            'total_unchanged': 14870
        },
        # ... other CSV types
    }
}
```

## Benefits

1. **Performance**: Only process changed data instead of entire dataset
2. **Efficiency**: Reduce Neo4j write operations by 90%+ on incremental updates
3. **Scalability**: Handle large datasets with minimal processing time
4. **Accuracy**: Detect and update only what changed

## SSE Messages

The Ingestion Wrangler broadcasts change detection progress:

```
Agent 1: Detecting new and updated records...
Agent 1: Change detection complete - 150 new, 50 updated, 14850 unchanged
```

## Next Steps

When implementing the Graph Architect agent (Task 4), ensure:

1. Use **MERGE** instead of **CREATE** for all node creation
2. Check `state['change_summary']` to optimize batch processing
3. Only process new/updated records from `state['change_summary']['details']`
4. Use UNWIND batching for efficient bulk operations

## Testing

To test incremental ingestion:

1. Upload CSV files for the first time
2. Modify a few records in the CSV files
3. Upload again
4. Check SSE messages for change detection results
5. Verify only changed records are processed

## Files Created

- `backend/utils/change_detection.py` - Change detection logic
- `backend/utils/db_connection.py` - PostgreSQL and Neo4j connection managers
- `backend/orchestration/agent_ingestion_wrangler.py` - Updated with incremental support
- `backend/orchestration/state.py` - Updated with change_summary field
