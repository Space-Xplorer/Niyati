# Migration from PostgreSQL to SQLite

## Summary

Project Niyati has been successfully migrated from PostgreSQL to SQLite for easier development setup. SQLite is a file-based database that requires no separate server installation.

## Changes Made

### 1. Environment Configuration (.env)

**Before:**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/postgres
```

**After:**
```env
DATABASE_URL=sqlite:///niyati.db
```

### 2. Database Models (models.py)

- Removed PostgreSQL-specific imports (`ARRAY`, `JSONB`)
- All models already used `db.JSON` which is compatible with SQLite
- No schema changes required

### 3. Docker Compose (docker-compose.yml)

- Removed PostgreSQL service
- Kept Neo4j service (still required for knowledge graph)
- SQLite doesn't need a container (file-based)

### 4. .gitignore

Added SQLite database files to .gitignore:
```
*.db
*.db-journal
*.db-shm
*.db-wal
```

### 5. Documentation

Updated README files to reflect SQLite usage:
- Main README.md
- backend/README.md

## Database File Location

The SQLite database is created as `niyati.db` in the `backend/` directory.

## Advantages of SQLite for Development

1. **No Installation Required** - SQLite is built into Python
2. **Zero Configuration** - No server setup, users, or permissions
3. **Portable** - Single file database
4. **Fast for Development** - No network overhead
5. **Easy Backup** - Just copy the .db file

## Limitations to Consider

1. **Concurrency** - SQLite has limited concurrent write support
2. **Scalability** - Not suitable for high-traffic production
3. **Network Access** - Cannot be accessed remotely
4. **Data Types** - Some PostgreSQL-specific types not available

## Migration Path to Production

When ready for production, you can easily migrate back to PostgreSQL:

1. Update `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@host:5432/database
   ```

2. Run migrations:
   ```bash
   python init_db.py
   ```

3. Export data from SQLite and import to PostgreSQL (if needed)

## Verification

Database was successfully initialized with all 9 tables:
- ✓ users
- ✓ raw_invoices
- ✓ raw_eway_bills
- ✓ entity_master
- ✓ engineered_features
- ✓ risk_predictions
- ✓ fraud_patterns
- ✓ audit_narratives
- ✓ shape_plots

## Testing

All existing functionality remains the same. The application code is database-agnostic thanks to SQLAlchemy ORM.

To verify the migration:
```bash
# Initialize database
python init_db.py

# Start the application
python main.py

# Test authentication
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","role":"Admin"}'
```

## Rollback (if needed)

To rollback to PostgreSQL:

1. Restore original `.env` with PostgreSQL connection string
2. Install PostgreSQL
3. Run `python init_db.py`
4. Restore data from backup

## Support

For issues related to SQLite, check:
- SQLite documentation: https://www.sqlite.org/docs.html
- SQLAlchemy SQLite dialect: https://docs.sqlalchemy.org/en/20/dialects/sqlite.html
