# Project Niyati - Dashboard Explanation

## Business Owner Dashboard Components

### 1. Health Score
**What it shows**: Overall compliance health (0-100)
- **Calculation**: 100 - (Risk Probability × 100)
- **Example**: If risk probability is 0.45 (45%), health score is 55/100

**What it means**:
- 70-100: Good compliance, low fraud risk
- 40-69: Moderate risk, needs attention
- 0-39: High risk, immediate action required

### 2. Risk Level
**What it shows**: Your fraud risk category
- **HIGH_RISK**: >65% probability of fraud involvement
- **MEDIUM_RISK**: 35-65% probability
- **LOW_RISK**: <35% probability

**Risk Factors**:
- KYC Score (lower = higher risk)
- Transaction patterns (too few or too many)
- Partner network (too many partners)
- Status (Active vs Inactive)

### 3. Fraud Indicators
Shows if you're involved in specific fraud patterns:

#### Circular Trade
- **What**: A→B→C→A trading pattern (goods/invoices go in a circle)
- **Why it's fraud**: Creates fake transactions to claim tax credits
- **Example**: You sell to Company B, B sells to Company C, C sells back to you
- **Impact**: All parties can be prosecuted for tax evasion

#### Ghost Invoices
- **What**: Invoices without corresponding e-way bills
- **Why it's fraud**: Fake invoices to claim Input Tax Credit
- **Example**: Invoice shows ₹10L transaction but no goods were actually moved
- **Impact**: ITC claims will be rejected, penalties applied

#### Spider Web Network
- **What**: Multiple companies sharing contact information
- **Why it's fraud**: Indicates shell companies or coordinated fraud
- **Example**: 10 companies all using the same phone number/email
- **Impact**: All companies flagged for investigation

### 4. Vendor Risk Analysis
**What it shows**: Risk levels of companies you do business with

**Columns**:
- **Vendor GSTIN**: Tax ID of your business partner
- **Vendor Name**: Company name (or last 4 digits of GSTIN)
- **Risk Level**: Their fraud risk (HIGH/MEDIUM/LOW)
- **ITC at Risk**: Input Tax Credit amount you could lose
- **Last Transaction**: Most recent transaction date

**Why it matters**:
1. **Guilt by Association**: If your vendors are fraudulent, you're at risk
2. **ITC Denial**: Tax department can deny your Input Tax Credit claims
3. **Audit Trigger**: High-risk vendors trigger audits of your business
4. **Legal Liability**: You could be held liable for their fraud

**Example Scenario**:
```
You buy goods from Vendor A (HIGH RISK)
- Vendor A is involved in circular trade
- You claimed ₹5L Input Tax Credit on purchases from A
- Tax department discovers A is fraudulent
- Your ₹5L ITC claim is DENIED
- You must pay back ₹5L + penalties + interest
```

### 5. Detailed Risk Assessment
**What it shows**: Complete analysis of your risk profile

**Includes**:
- Business profile (sector, KYC, transactions)
- Fraud involvement details
- List of partners in circular trade
- Specific recommendations

**Example Output**:
```
FRAUD INDICATORS:
- Circular Trade: YES - 2 circular paths detected
  Partners: 27AAAAA8421A1Z2, 27AAAAA9844A1Z206
- Ghost Invoices: 15 invoices without e-way bills
- Shared Contact Network: 8 entities with shared contacts

RECOMMENDATIONS:
- URGENT: You are involved in 2 circular trade patterns
- WARNING: 15 invoices lack e-way bill backing
- Maintain proper documentation for all transactions
```

## Graph Visualization

### Node Types
1. **Taxpayer** (circles)
   - Red: HIGH_RISK
   - Orange: MEDIUM_RISK
   - Green: LOW_RISK
   - Gray: Unknown risk

2. **Invoice** (gray squares)
   - Represents transactions

3. **EwayBill** (gray triangles)
   - Represents goods movement

### Edge Types
1. **ISSUED**: Taxpayer → Invoice (company issued invoice)
2. **TO**: Invoice → Taxpayer (invoice sent to company)
3. **BACKED_BY**: Invoice → EwayBill (invoice has e-way bill)
4. **SHARED_CONTACT**: Taxpayer → Taxpayer (shared contact info)

### Cycle Detection
**What to look for**:
- **Circular Trade**: Taxpayer A → Invoice → Taxpayer B → Invoice → Taxpayer A
- **Spider Web**: Multiple taxpayers connected via SHARED_CONTACT
- **Ghost Invoices**: Invoices without BACKED_BY edges to EwayBills

## How Risk is Calculated

### Risk Score Formula
```
Base Risk = 0.3

+ KYC Factor = (100 - KYC_Score) / 200 × 0.4
  (Lower KYC = Higher Risk)

+ Status Factor = 0.15 if Status != 'Active'
  (Inactive companies are suspicious)

+ Transaction Factor = 0.2 if transactions == 0 or > 50
  (Too few or too many transactions)

+ Partner Factor = 0.1 if unique_partners > 20
  (Too many partners is suspicious)

+ Random Variation = -0.15 to +0.15
  (Adds realistic distribution)

Final Risk Score = Clamp(Total, 0.05, 0.95)
```

### Risk Level Thresholds
- **HIGH_RISK**: Risk Score > 0.65 (65%)
- **MEDIUM_RISK**: Risk Score 0.35-0.65 (35-65%)
- **LOW_RISK**: Risk Score < 0.35 (35%)

## Action Items Based on Risk Level

### HIGH RISK
1. **Immediate Actions**:
   - Review all transactions with flagged vendors
   - Verify e-way bills for all invoices
   - Check for circular trade involvement
   - Prepare documentation for audit

2. **Long-term**:
   - Stop transactions with HIGH RISK vendors
   - Improve KYC processes
   - Implement transaction monitoring
   - Regular compliance audits

### MEDIUM RISK
1. **Review**:
   - Verify vendor credentials
   - Ensure all invoices have e-way bills
   - Monitor transaction patterns

2. **Improve**:
   - Strengthen KYC procedures
   - Diversify vendor base
   - Maintain proper documentation

### LOW RISK
1. **Maintain**:
   - Continue current practices
   - Regular compliance checks
   - Keep documentation updated

## Understanding the Data Source

The dashboard shows: **Data Source: NEO4J (Computed On-The-Fly)**

This means:
- Risk scores are calculated in real-time from graph data
- No pre-computed scores stored in database
- Always reflects latest transaction patterns
- Fraud patterns detected from actual relationships

## Key Takeaways

1. **Vendor Risk Matters**: Your vendors' fraud affects YOUR business
2. **Circular Trade is Serious**: Can result in prosecution
3. **Ghost Invoices = ITC Denial**: Fake invoices lose you money
4. **Documentation is Critical**: E-way bills prove legitimacy
5. **Monitor Regularly**: Risk changes as you transact

## Next Steps

1. **Review Vendor List**: Check all HIGH RISK vendors
2. **Verify Invoices**: Ensure all have e-way bills
3. **Check Circular Trade**: If flagged, investigate immediately
4. **Improve KYC**: Better vendor verification
5. **Regular Monitoring**: Check dashboard weekly
