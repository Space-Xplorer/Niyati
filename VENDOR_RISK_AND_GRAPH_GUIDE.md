# Vendor Risk Analysis & Graph Visualization Guide

## What is Vendor Risk Analysis?

The Vendor Risk Analysis table shows the **fraud risk levels of companies you do business with**. This is critical because:

### Why Vendor Risk Matters

1. **Guilt by Association**: If your vendors are involved in fraud, tax authorities may investigate you
2. **ITC Denial**: Input Tax Credit claims from fraudulent vendors will be rejected
3. **Financial Loss**: You could lose the ITC amount + penalties + interest
4. **Legal Liability**: You may be held liable for your vendors' fraudulent activities
5. **Audit Trigger**: High-risk vendors automatically trigger audits of your business

### Vendor Risk Table Columns

| Column | Description | What It Means |
|--------|-------------|---------------|
| **Vendor GSTIN** | Tax ID of your business partner | Unique identifier for the company |
| **Vendor Name** | Company name | Name of the entity (or last 4 digits of GSTIN) |
| **Risk Level** | HIGH / MEDIUM / LOW | Fraud probability of this vendor |
| **ITC at Risk** | Amount in ₹ | Input Tax Credit you could lose if vendor is fraudulent |
| **Last Transaction** | Date | Most recent transaction with this vendor |

### Risk Level Meanings

- **HIGH RISK** (Red): >65% fraud probability
  - Immediate action required
  - Stop transactions with this vendor
  - Review all past transactions
  - Prepare documentation for audit

- **MEDIUM RISK** (Yellow): 35-65% fraud probability
  - Monitor closely
  - Verify vendor credentials
  - Ensure proper documentation
  - Consider alternative vendors

- **LOW RISK** (Green): <35% fraud probability
  - Continue normal operations
  - Maintain regular compliance checks
  - Keep documentation updated

### Example Scenario

```
Vendor: Entity Z281 (27AAAAA8413A1Z281)
Risk Level: HIGH RISK
ITC at Risk: ₹1,91,521
Last Transaction: 8 Dec 2025

What this means:
- This vendor has >65% probability of fraud involvement
- You claimed ₹1,91,521 Input Tax Credit on purchases from them
- If tax department discovers they're fraudulent:
  → Your ₹1,91,521 ITC claim will be DENIED
  → You must pay back ₹1,91,521 + penalties + interest
  → Your business will be audited
  → You may face legal action

Action Required:
1. STOP all transactions with this vendor immediately
2. Review all past invoices and e-way bills
3. Verify if goods were actually received
4. Prepare documentation for tax authorities
5. Consult with tax advisor
```

## Graph Visualization

### What the Graph Shows

The graph visualization displays the **network of relationships** between taxpayers, invoices, and e-way bills. It helps identify:

1. **Circular Trade Patterns**: Companies trading in circles to create fake transactions
2. **Spider Web Networks**: Multiple companies sharing contact information (shell companies)
3. **Ghost Invoices**: Invoices without corresponding e-way bills
4. **Transaction Flows**: How money and goods move through the network

### Node Types

#### 1. Taxpayer Nodes (Circles)
- **Red**: HIGH RISK (>65% fraud probability)
- **Orange**: MEDIUM RISK (35-65% fraud probability)
- **Green**: LOW RISK (<35% fraud probability)
- **Gray**: Unknown risk level

**Pulsing Red Ring**: Node is involved in circular trade or cycle

#### 2. Invoice Nodes (Gray Squares)
- Represents transaction documents
- Shows invoice value and date
- Can be part of circular trade cycles

#### 3. E-Way Bill Nodes (Gray Triangles)
- Represents goods movement documentation
- Proves physical goods were transported
- Missing e-way bills indicate ghost invoices

### Edge Types (Relationships)

| Edge Type | Description | What It Means |
|-----------|-------------|---------------|
| **ISSUED** | Taxpayer → Invoice | Company issued this invoice |
| **TO** | Invoice → Taxpayer | Invoice sent to this company |
| **BACKED_BY** | Invoice → EwayBill | Invoice has e-way bill (legitimate) |
| **SHARED_CONTACT** | Taxpayer → Taxpayer | Companies share contact info (suspicious) |

### Cycle Detection

The graph automatically detects and highlights **circular trade patterns**:

#### What is a Cycle?
A cycle occurs when transactions form a closed loop:
```
Company A → Invoice → Company B → Invoice → Company C → Invoice → Company A
```

#### Why Cycles are Fraudulent
1. **Fake Transactions**: Goods/invoices go in a circle, creating fake tax credits
2. **Tax Evasion**: All parties claim Input Tax Credit on fake transactions
3. **Money Laundering**: Used to move money illegally
4. **Prosecution Risk**: All parties can be prosecuted for tax fraud

#### How Cycles are Shown
- **Pulsing Red Nodes**: Nodes involved in cycles pulse with red animation
- **Red Edges**: Edges that are part of cycles are highlighted in red
- **Thicker Lines**: Cycle edges are thicker (2.5px vs 1.5px)
- **Cycle Counter**: Shows total number of nodes involved in cycles

### Graph Statistics

The legend shows:
- **Nodes**: Total number of entities in the graph
- **Edges**: Total number of relationships
- **Cycle Nodes**: Number of nodes involved in circular trade (if any)

### Interpreting the Graph

#### Healthy Network
```
- Few or no cycles
- Most nodes are green (low risk)
- Invoices have BACKED_BY edges to e-way bills
- No dense clusters of SHARED_CONTACT edges
```

#### Suspicious Network
```
- Multiple cycles detected
- Many red nodes (high risk)
- Invoices without BACKED_BY edges (ghost invoices)
- Dense SHARED_CONTACT clusters (spider web)
```

### Example Fraud Patterns

#### 1. Circular Trade
```
Taxpayer A (Red, Pulsing)
    ↓ ISSUED
Invoice 1
    ↓ TO
Taxpayer B (Red, Pulsing)
    ↓ ISSUED
Invoice 2
    ↓ TO
Taxpayer A (Red, Pulsing)  ← CYCLE DETECTED
```

**What this means**: A and B are creating fake transactions in a loop

#### 2. Ghost Invoices
```
Taxpayer A
    ↓ ISSUED
Invoice 1 (No BACKED_BY edge)
    ↓ TO
Taxpayer B
```

**What this means**: Invoice exists but no goods were moved (no e-way bill)

#### 3. Spider Web Network
```
Taxpayer A ←→ SHARED_CONTACT ←→ Taxpayer B
     ↕                              ↕
SHARED_CONTACT                 SHARED_CONTACT
     ↕                              ↕
Taxpayer C ←→ SHARED_CONTACT ←→ Taxpayer D
```

**What this means**: All 4 companies share contact info (likely shell companies)

## Business Owner Dashboard

### What You See

1. **Health Score**: Your overall compliance health (0-100)
   - Calculated as: 100 - (Risk Probability × 100)
   - Lower score = higher fraud risk

2. **Risk Level**: Your fraud risk category
   - Based on KYC score, transaction patterns, partner network

3. **Fraud Indicators**:
   - **Circular Trade Patterns**: Number of circular paths you're involved in
   - **Ghost Invoices**: Invoices without e-way bills
   - **Spider Web Involvement**: Whether you're in a shared contact network

4. **Vendor Risk Analysis**: Risk levels of your business partners
   - Click any row to see detailed risk narrative
   - Shows ITC amount at risk for each vendor

5. **Detailed Risk Assessment**: Complete analysis with:
   - Business profile
   - Fraud involvement details
   - List of partners in circular trade
   - Specific recommendations

### Action Items by Risk Level

#### HIGH RISK (Score < 35)
```
IMMEDIATE ACTIONS:
1. Review all transactions with flagged vendors
2. Verify e-way bills for all invoices
3. Check for circular trade involvement
4. Prepare documentation for audit
5. Stop transactions with HIGH RISK vendors

LONG-TERM:
1. Improve KYC processes
2. Implement transaction monitoring
3. Regular compliance audits
4. Diversify vendor base
```

#### MEDIUM RISK (Score 35-69)
```
REVIEW:
1. Verify vendor credentials
2. Ensure all invoices have e-way bills
3. Monitor transaction patterns

IMPROVE:
1. Strengthen KYC procedures
2. Maintain proper documentation
3. Regular compliance checks
```

#### LOW RISK (Score 70-100)
```
MAINTAIN:
1. Continue current practices
2. Regular compliance checks
3. Keep documentation updated
```

## Admin Dashboard (Government Officers)

### What You See

1. **System Health Overview**:
   - Overall health score across all taxpayers
   - Total taxpayers in system
   - Records processed today
   - Alerts generated today

2. **Risk Distribution**:
   - Count of HIGH / MEDIUM / LOW risk taxpayers
   - Percentage breakdown

3. **Structural Fraud Patterns**:
   - **Circular Trade**: Number of circular trade patterns detected
   - **Ghost Invoices**: Total invoices without e-way bills
   - **Spider Web Networks**: Number of shared contact networks

4. **Fraud Details Tables**:
   - Click tabs to see specific GSTINs involved in each fraud type
   - **Circular Trade Tab**: Shows GSTIN pairs in circular trade
   - **Ghost Invoices Tab**: Shows GSTINs with ghost invoice counts
   - **Spider Web Tab**: Shows GSTINs with shared contact counts

5. **Vendor Risk Analysis**:
   - System-wide view of all taxpayers and their risk levels
   - Click any row to see detailed risk narrative

### Investigation Workflow

```
1. Review System Health Overview
   → Identify high-risk areas

2. Check Fraud Pattern Counts
   → See which fraud types are most prevalent

3. Click Fraud Pattern Tabs
   → Get specific GSTINs involved

4. Review Vendor Risk Table
   → Sort by risk level to prioritize investigations

5. Click on High-Risk Entities
   → Read detailed risk narratives

6. View Network Graph
   → Visualize relationships and cycles

7. Initiate Audits
   → Focus on entities in cycles or with high fraud indicators
```

## Key Takeaways

1. **Vendor Risk Directly Affects You**: Your vendors' fraud becomes your problem
2. **Cycles = Serious Fraud**: Circular trade can result in prosecution
3. **Ghost Invoices = ITC Denial**: Fake invoices lose you money
4. **Documentation is Critical**: E-way bills prove transaction legitimacy
5. **Monitor Regularly**: Risk changes as you transact
6. **Graph Shows Truth**: Visual patterns reveal hidden fraud networks
7. **Act on High Risk**: Don't wait - investigate and stop transactions immediately

## Technical Details

### Data Source
- **Risk Scores**: Calculated on-the-fly from Neo4j graph data
- **Fraud Patterns**: Detected using Cypher queries on Neo4j
- **Graph Structure**: Stored in Neo4j graph database
- **Real-time**: All data reflects current state of the network

### Risk Calculation Formula
```
Base Risk = 0.3

+ KYC Factor = (100 - KYC_Score) / 200 × 0.4
+ Status Factor = 0.15 if Status != 'Active'
+ Transaction Factor = 0.2 if transactions == 0 or > 50
+ Partner Factor = 0.1 if unique_partners > 20
+ Random Variation = -0.15 to +0.15

Final Risk Score = Clamp(Total, 0.05, 0.95)

Risk Level:
- HIGH_RISK: Score > 0.65
- MEDIUM_RISK: Score 0.35-0.65
- LOW_RISK: Score < 0.35
```

### Cycle Detection Algorithm
```
1. Build adjacency list from edges
2. Perform DFS (Depth-First Search) on all nodes
3. Track visited nodes and recursion stack
4. When a node in recursion stack is revisited, cycle detected
5. Mark all nodes in the cycle path
6. Highlight cycle nodes and edges in visualization
```

## Support

For questions or issues:
1. Review this guide
2. Check DASHBOARD_EXPLANATION.md for more details
3. Contact system administrator
4. Consult with tax advisor for legal matters
