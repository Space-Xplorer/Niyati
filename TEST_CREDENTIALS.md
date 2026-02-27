# Test Credentials for Project Niyati

## Admin User (Government Officer)
- **Email**: admin@gstn.gov.in
- **Password**: admin123
- **Role**: Admin
- **Access**: System-wide view, all taxpayers, fraud patterns, network graph

## Business Owner Users (Taxpayers)

### Business Owner 1
- **Email**: business1@example.com
- **Password**: business123
- **Role**: Business_Owner
- **GSTIN**: 27AAAAA7009A1Z0
- **Access**: Own risk assessment, upload data, 2-hop network graph

### Business Owner 2
- **Email**: business2@example.com
- **Password**: business123
- **Role**: Business_Owner
- **GSTIN**: 27AAAAA5558A1Z1
- **Access**: Own risk assessment, upload data, 2-hop network graph

### Taxpayer
- **Email**: taxpayer@example.com
- **Password**: taxpayer123
- **Role**: Business_Owner
- **GSTIN**: 27AAAAA8421A1Z2
- **Access**: Own risk assessment, upload data, 2-hop network graph

## Role-Based Access Control (RBAC)

### Admin Role
- View all taxpayers and their risk scores
- Access system-wide fraud patterns
- View complete network graph (2000+ nodes)
- Cannot upload data (view-only)

### Business_Owner Role
- View only their own risk assessment
- Upload CSV files (invoices, e-way bills)
- View 2-hop neighborhood in network graph
- Access to upload functionality

## Testing RBAC

1. **Login as Admin**: See admin dashboard with all taxpayers
2. **Login as Business Owner**: See personal dashboard with own GSTIN
3. **Try to access other GSTIN data**: Should be denied (403 Forbidden)

## Notes

- All passwords are for testing only
- In production, use strong passwords and proper authentication
- Admin users should not have GSTIN (they're government officers)
- Business owners must have valid GSTIN
