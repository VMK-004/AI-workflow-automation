# PostgreSQL Migration Verification Checklist

**Migration Date:** December 3, 2025  
**Project:** AI Workflow Builder Platform  
**Migration From:** SQLite (`sqlite+aiosqlite:///./ai_workflow_builder.db`)  
**Migration To:** PostgreSQL (`postgresql+asyncpg://postgres:postgres@localhost:5432/ai_workflow_builder`)

---

## 1. Schema & Data Integrity Checks

### Table Row Count Comparison

Compare row counts for each table between SQLite and PostgreSQL to ensure they match:

- [ ] **users** - Row count comparison

  ```sql
  -- SQLite
  SELECT COUNT(*) FROM users;

  -- PostgreSQL
  SELECT COUNT(*) FROM users;
  ```

  **Expected:** Counts match exactly

- [ ] **workflows** - Row count comparison

  ```sql
  -- SQLite
  SELECT COUNT(*) FROM workflows;

  -- PostgreSQL
  SELECT COUNT(*) FROM workflows;
  ```

  **Expected:** Counts match exactly

- [ ] **nodes** - Row count comparison

  ```sql
  -- SQLite
  SELECT COUNT(*) FROM nodes;

  -- PostgreSQL
  SELECT COUNT(*) FROM nodes;
  ```

  **Expected:** Counts match exactly

- [ ] **edges** - Row count comparison

  ```sql
  -- SQLite
  SELECT COUNT(*) FROM edges;

  -- PostgreSQL
  SELECT COUNT(*) FROM edges;
  ```

  **Expected:** Counts match exactly

- [ ] **workflow_runs** - Row count comparison

  ```sql
  -- SQLite
  SELECT COUNT(*) FROM workflow_runs;

  -- PostgreSQL
  SELECT COUNT(*) FROM workflow_runs;
  ```

  **Expected:** Counts match exactly

- [ ] **node_executions** - Row count comparison

  ```sql
  -- SQLite
  SELECT COUNT(*) FROM node_executions;

  -- PostgreSQL
  SELECT COUNT(*) FROM node_executions;
  ```

  **Expected:** Counts match exactly

- [ ] **vector_collections** - Row count comparison

  ```sql
  -- SQLite
  SELECT COUNT(*) FROM vector_collections;

  -- PostgreSQL
  SELECT COUNT(*) FROM vector_collections;
  ```

  **Expected:** Counts match exactly

### Sample Record Comparison

For a sample of rows from each table, compare all column values between old vs new database:

- [ ] **users table** - Compare full records for 3-5 sample users

  ```sql
  -- SQLite
  SELECT * FROM users WHERE id IN ('user_id_1', 'user_id_2', 'user_id_3');

  -- PostgreSQL
  SELECT * FROM users WHERE id IN ('user_id_1', 'user_id_2', 'user_id_3');
  ```

  **Verify:** id, username, email, hashed_password, is_active, created_at, updated_at all match

- [ ] **workflows table** - Compare full records for 3-5 sample workflows

  ```sql
  -- SQLite
  SELECT * FROM workflows WHERE id IN ('workflow_id_1', 'workflow_id_2');

  -- PostgreSQL
  SELECT * FROM workflows WHERE id IN ('workflow_id_1', 'workflow_id_2');
  ```

  **Verify:** id, user_id, name, description, is_active, created_at, updated_at all match

- [ ] **nodes table** - Compare full records including JSON/config fields

  ```sql
  -- SQLite
  SELECT * FROM nodes WHERE workflow_id = 'workflow_id';

  -- PostgreSQL
  SELECT * FROM nodes WHERE workflow_id = 'workflow_id';
  ```

  **Verify:** id, workflow_id, name, node_type, config (JSON), position_x, position_y all match

- [ ] **edges table** - Compare full records

  ```sql
  -- SQLite
  SELECT * FROM edges WHERE workflow_id = 'workflow_id';

  -- PostgreSQL
  SELECT * FROM edges WHERE workflow_id = 'workflow_id';
  ```

  **Verify:** id, workflow_id, source_node_id, target_node_id all match

- [ ] **workflow_runs table** - Compare execution records

  ```sql
  -- SQLite
  SELECT * FROM workflow_runs WHERE id = 'run_id';

  -- PostgreSQL
  SELECT * FROM workflow_runs WHERE id = 'run_id';
  ```

  **Verify:** id, workflow_id, user_id, status, started_at, completed_at, results (JSON) all match

- [ ] **node_executions table** - Compare execution details

  ```sql
  -- SQLite
  SELECT * FROM node_executions WHERE workflow_run_id = 'run_id';

  -- PostgreSQL
  SELECT * FROM node_executions WHERE workflow_run_id = 'run_id';
  ```

  **Verify:** id, workflow_run_id, node_id, status, input_data (JSON), output_data (JSON) all match

- [ ] **vector_collections table** - Compare vector metadata

  ```sql
  -- SQLite
  SELECT * FROM vector_collections WHERE id = 'collection_id';

  -- PostgreSQL
  SELECT * FROM vector_collections WHERE id = 'collection_id';
  ```

  **Verify:** id, user_id, name, dimension, index_path, document_count, created_at all match

### Foreign-Key Relationships & Referential Integrity

Verify foreign-key relationships and referential integrity - ensure no orphaned records:

- [ ] **users → workflows** - Verify all workflows have valid user_id

  ```sql
  -- PostgreSQL
  SELECT w.* FROM workflows w
  LEFT JOIN users u ON w.user_id = u.id
  WHERE u.id IS NULL;
  ```

  **Expected:** 0 rows (no orphaned workflows)

- [ ] **workflows → nodes** - Verify all nodes have valid workflow_id

  ```sql
  -- PostgreSQL
  SELECT n.* FROM nodes n
  LEFT JOIN workflows w ON n.workflow_id = w.id
  WHERE w.id IS NULL;
  ```

  **Expected:** 0 rows (no orphaned nodes)

- [ ] **workflows → edges** - Verify all edges have valid workflow_id and node references

  ```sql
  -- PostgreSQL
  SELECT e.* FROM edges e
  LEFT JOIN workflows w ON e.workflow_id = w.id
  LEFT JOIN nodes n1 ON e.source_node_id = n1.id
  LEFT JOIN nodes n2 ON e.target_node_id = n2.id
  WHERE w.id IS NULL OR n1.id IS NULL OR n2.id IS NULL;
  ```

  **Expected:** 0 rows (no orphaned edges)

- [ ] **workflows → workflow_runs** - Verify all runs have valid workflow_id and user_id

  ```sql
  -- PostgreSQL
  SELECT wr.* FROM workflow_runs wr
  LEFT JOIN workflows w ON wr.workflow_id = w.id
  LEFT JOIN users u ON wr.user_id = u.id
  WHERE w.id IS NULL OR u.id IS NULL;
  ```

  **Expected:** 0 rows (no orphaned workflow runs)

- [ ] **workflow_runs → node_executions** - Verify all node executions have valid run_id and node_id

  ```sql
  -- PostgreSQL
  SELECT ne.* FROM node_executions ne
  LEFT JOIN workflow_runs wr ON ne.workflow_run_id = wr.id
  LEFT JOIN nodes n ON ne.node_id = n.id
  WHERE wr.id IS NULL OR n.id IS NULL;
  ```

  **Expected:** 0 rows (no orphaned node executions)

- [ ] **users → vector_collections** - Verify all collections have valid user_id

  ```sql
  -- PostgreSQL
  SELECT vc.* FROM vector_collections vc
  LEFT JOIN users u ON vc.user_id = u.id
  WHERE u.id IS NULL;
  ```

  **Expected:** 0 rows (no orphaned vector collections)

- [ ] **Verify foreign key constraints exist**
  ```sql
  SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
  FROM information_schema.table_constraints AS tc
  JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
  JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
  WHERE tc.constraint_type = 'FOREIGN KEY'
  ORDER BY tc.table_name, kcu.column_name;
  ```
  **Expected:** All expected foreign key constraints are present

### Data Types & Columns Verification

Check data types / columns - ensure types are correctly migrated and values preserved:

- [ ] **UUID/String IDs** - Verify all id fields (String(36)) preserved correctly

  ```sql
  -- PostgreSQL - Check UUID format
  SELECT id FROM users WHERE id !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$';
  ```

  **Expected:** 0 rows (all IDs are valid UUID format)

- [ ] **JSON Fields** - Verify JSON/JSONB fields preserved correctly

  - [ ] **nodes.config** - JSON field for node configuration
    ```sql
    SELECT id, config::json FROM nodes WHERE config IS NOT NULL LIMIT 5;
    ```
  - [ ] **workflow_runs.results** - JSON field for execution results
    ```sql
    SELECT id, results::json FROM workflow_runs WHERE results IS NOT NULL LIMIT 5;
    ```
  - [ ] **node_executions.input_data** - JSON field
    ```sql
    SELECT id, input_data::json FROM node_executions WHERE input_data IS NOT NULL LIMIT 5;
    ```
  - [ ] **node_executions.output_data** - JSON field
    ```sql
    SELECT id, output_data::json FROM node_executions WHERE output_data IS NOT NULL LIMIT 5;
    ```
    **Expected:** All JSON fields parse correctly

- [ ] **DateTime Fields** - Verify timestamps preserved correctly

  ```sql
  -- Check created_at, updated_at in all tables
  SELECT id, created_at, updated_at FROM users LIMIT 5;
  SELECT id, created_at, updated_at FROM workflows LIMIT 5;
  ```

  **Expected:** All timestamps are valid, timezone handling is correct (UTC)

- [ ] **Text Fields** - Verify long text fields preserved

  ```sql
  -- workflows.description (Text type)
  SELECT id, description, LENGTH(description) as desc_length
  FROM workflows
  WHERE description IS NOT NULL
  ORDER BY desc_length DESC
  LIMIT 5;
  ```

  **Expected:** Text fields preserved, no truncation

- [ ] **Boolean Fields** - Verify boolean values preserved

  ```sql
  SELECT id, is_active FROM users;
  SELECT id, is_active FROM workflows;
  ```

  **Expected:** All boolean values are true/false (not null/0/1)

- [ ] **Numeric Fields** - Verify numeric types preserved
  ```sql
  -- vector_collections.dimension (Integer)
  SELECT id, dimension FROM vector_collections;
  -- nodes.position_x, position_y (Float)
  SELECT id, position_x, position_y FROM nodes LIMIT 5;
  ```
  **Expected:** Numeric values match exactly

---

## 2. Application Compatibility & Functionality Tests

### Backend Test Suite Execution

Run the complete backend test suite to ensure everything works as expected under PostgreSQL:

- [ ] **Run all tests**

  ```bash
  cd backend
  pytest tests/ -v
  ```

  **Expected:** All tests pass

- [ ] **Run authentication tests**

  ```bash
  pytest tests/test_auth.py -v
  ```

  **Expected:** User registration, login, token generation work correctly

- [ ] **Run workflow tests**

  ```bash
  pytest tests/test_workflows.py -v
  ```

  **Expected:** Workflow CRUD operations work correctly

- [ ] **Run execution tests**
  ```bash
  pytest tests/test_execution.py -v
  ```
  **Expected:** Workflow execution engine works correctly

### Manual CRUD Endpoint Testing

Test creation, update, deletion flows for all data models:

- [ ] **User CRUD Operations**

  - [ ] Create user via API
    ```bash
    curl -X POST http://localhost:8000/api/auth/register \
      -H "Content-Type: application/json" \
      -d '{"username":"testuser","email":"test@example.com","password":"testpass123"}'
    ```
  - [ ] Read user - Verify user appears in PostgreSQL
  - [ ] Update user - Verify changes persist
  - [ ] Delete user - Verify cascade deletes work (workflows, runs, collections)

- [ ] **Workflow CRUD Operations**

  - [ ] Create workflow
    ```bash
    curl -X POST http://localhost:8000/api/workflows \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"name":"Test Workflow","description":"Test description"}'
    ```
  - [ ] Read workflow - Verify data retrieved correctly
  - [ ] Update workflow - Verify changes saved
  - [ ] Delete workflow - Verify cascade deletes (nodes, edges)

- [ ] **Node CRUD Operations**

  - [ ] Create node
    ```bash
    curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"name":"test_node","node_type":"llm_call","config":{"prompt":"test"}}'
    ```
  - [ ] Read node - Verify JSON config field works
  - [ ] Update node - Verify changes persist
  - [ ] Delete node - Verify cleanup

- [ ] **Edge CRUD Operations**

  - [ ] Create edge
    ```bash
    curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/edges \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"source_node_id":"node1","target_node_id":"node2"}'
    ```
  - [ ] Read edges - Verify relationships correct
  - [ ] Delete edge - Verify cleanup

- [ ] **Workflow Run Operations**

  - [ ] Execute workflow
    ```bash
    curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/execute \
      -H "Authorization: Bearer $TOKEN"
    ```
  - [ ] View run history - Verify runs saved and retrieved
  - [ ] View node executions - Verify execution details logged

- [ ] **Vector Collection CRUD Operations**
  - [ ] Create collection
    ```bash
    curl -X POST http://localhost:8000/api/vectors/collections \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"name":"test_collection","description":"test","dimension":384}'
    ```
  - [ ] List collections - Verify retrieval works
  - [ ] Update collection - Verify changes persist
  - [ ] Delete collection - Verify cleanup

### Code Reference Verification

Confirm that no code still references the old SQLite file path:

- [ ] **Check for SQLite references in code**

  ```bash
  cd backend
  grep -r "sqlite" app/ scripts/ --exclude-dir=__pycache__
  grep -r "ai_workflow_builder.db" app/ scripts/ --exclude-dir=__pycache__
  ```

  **Expected:** Only comments, documentation, or test configurations found

- [ ] **Verify DATABASE_URL usage**

  ```python
  from app.core.config import settings
  print(settings.DATABASE_URL)
  # Should output: postgresql+asyncpg://...
  ```

  **Expected:** PostgreSQL connection string, no SQLite paths

- [ ] **Check database connection code**
  ```bash
  grep -r "create_async_engine" app/ --exclude-dir=__pycache__
  ```
  **Expected:** All use `settings.DATABASE_URL` (no hardcoded paths)

### Migration Configuration Verification

Check that migrations (via Alembic) are configured correctly:

- [ ] **Verify migration files exist**

  ```bash
  ls -la backend/alembic/versions/
  ```

  **Expected:** Initial migration file(s) present

- [ ] **Check current migration version**

  ```bash
  cd backend
  alembic current
  ```

  **Expected:** Shows current migration version

- [ ] **Verify all tables exist**

  ```sql
  SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
  ```

  **Expected tables:**

  - alembic_version
  - users
  - workflows
  - nodes
  - edges
  - workflow_runs
  - node_executions
  - vector_collections

- [ ] **Check Alembic version table**

  ```sql
  SELECT * FROM alembic_version;
  ```

  **Expected:** Current migration version recorded

- [ ] **Verify schema matches models**

  ```bash
  # Compare table structures
  docker exec ai-workflow-postgres psql -U postgres -d ai_workflow_builder -c "\d users"
  docker exec ai-workflow-postgres psql -U postgres -d ai_workflow_builder -c "\d workflows"
  ```

  **Expected:** Table structures match model definitions

- [ ] **Test migration rollback and re-apply**
  ```bash
  cd backend
  alembic downgrade -1
  alembic upgrade head
  ```
  **Expected:** Rollback and re-apply works without errors

---

## 3. Performance & Concurrency Tests (Optional but Recommended)

### Concurrent Request Testing

Perform simple load tests / concurrent requests to ensure PostgreSQL handles concurrency:

- [ ] **Test simultaneous reads**

  - Open two terminals
  - Run two simultaneous GET requests for workflows
  - **Expected:** Both succeed, no locking issues, proper response times

- [ ] **Test read-write concurrency**

  - Terminal 1: Create workflow (POST)
  - Terminal 2: List workflows (GET) at same time
  - **Expected:** No errors, proper transaction isolation, both operations succeed

- [ ] **Test write-write concurrency**

  - Terminal 1: Update workflow (PUT)
  - Terminal 2: Update same workflow (PUT) at same time
  - **Expected:** Proper conflict handling or last-write-wins, no data corruption

- [ ] **Test concurrent workflow executions**
  - Execute the same workflow multiple times simultaneously
  - **Expected:** All executions complete successfully, data integrity maintained

### Query Performance Testing

Execute typical queries and compare response times:

- [ ] **Fetch workflows list** - Measure response time

  ```bash
  time curl http://localhost:8000/api/workflows \
    -H "Authorization: Bearer $TOKEN"
  ```

  **Baseline:** < 500ms for typical dataset

- [ ] **Fetch single workflow with nodes/edges** - Measure response time

  ```bash
  time curl http://localhost:8000/api/workflows/$WORKFLOW_ID \
    -H "Authorization: Bearer $TOKEN"
  ```

  **Baseline:** < 300ms

- [ ] **Fetch run history** - Measure response time

  ```bash
  time curl http://localhost:8000/api/workflows/$WORKFLOW_ID/runs \
    -H "Authorization: Bearer $TOKEN"
  ```

  **Baseline:** < 400ms

- [ ] **Vector collection queries** - Measure response time

  ```bash
  time curl http://localhost:8000/api/vectors/collections \
    -H "Authorization: Bearer $TOKEN"
  ```

  **Baseline:** < 300ms

- [ ] **Complex query with joins** - Measure execution time

  ```sql
  EXPLAIN ANALYZE
  SELECT w.*, COUNT(n.id) as node_count, COUNT(e.id) as edge_count
  FROM workflows w
  LEFT JOIN nodes n ON w.id = n.workflow_id
  LEFT JOIN edges e ON w.id = e.workflow_id
  WHERE w.user_id = 'user_id'
  GROUP BY w.id;
  ```

  **Expected:** Query completes efficiently, execution plan is reasonable

- [ ] **Search/filter operations** - Test filtering workflows
  ```bash
  time curl "http://localhost:8000/api/workflows?is_active=true" \
    -H "Authorization: Bearer $TOKEN"
  ```
  **Expected:** Filtering works, response time acceptable

### Connection Pooling Verification

- [ ] **Check connection pool settings**

  ```python
  from app.db.database import engine
  print(f"Pool size: {engine.pool.size()}")
  print(f"Checked in: {engine.pool.checkedin()}")
  print(f"Checked out: {engine.pool.checkedout()}")
  ```

  **Expected:** Connection pool configured and working

- [ ] **Monitor connection leaks**
  - Run application for 10-15 minutes with normal load
  - Check PostgreSQL connections:
    ```sql
    SELECT count(*) FROM pg_stat_activity WHERE datname = 'ai_workflow_builder';
    ```
  - **Expected:** Connection count doesn't continuously grow

---

## 4. Environment & Configuration Verification

### DATABASE_URL Configuration

Ensure environment variable `DATABASE_URL` is set properly:

- [ ] **Check .env file**

  ```bash
  cat backend/.env | grep DATABASE_URL
  ```

  **Expected:** `DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname`

- [ ] **Verify .env.example**

  ```bash
  cat backend/.env.example | grep DATABASE_URL
  ```

  **Expected:** PostgreSQL template with placeholders

- [ ] **Test environment variable loading**

  ```bash
  export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_workflow_builder
  python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
  ```

  **Expected:** Environment variable takes precedence

- [ ] **Verify connection string format**
  - Format: `postgresql+asyncpg://username:password@host:port/database_name`
  - **Expected:** All components present and correct

### Application Startup & Connection

Confirm application starts without errors and connects successfully:

- [ ] **Start application**

  ```bash
  cd backend
  uvicorn app.main:app --reload
  ```

  **Expected:** Application starts, connects to PostgreSQL, no errors

- [ ] **Test database connection**

  ```bash
  python scripts/setup_postgres.py
  ```

  **Expected:** Connection successful, database accessible

- [ ] **Check application logs**

  ```bash
  # Look for database connection errors
  # Check startup messages
  ```

  **Expected:** No connection errors, successful startup

- [ ] **Test health endpoint**
  ```bash
  curl http://localhost:8000/health
  ```
  **Expected:** `{"status":"healthy"}`

### Migration Testing from Clean State

Validate that migrations run smoothly from a clean state:

- [ ] **Create fresh test database**

  ```bash
  docker exec ai-workflow-postgres psql -U postgres -c "CREATE DATABASE ai_workflow_builder_test;"
  ```

- [ ] **Update DATABASE_URL to test database**

  ```bash
  export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_workflow_builder_test
  ```

- [ ] **Run migrations on fresh database**

  ```bash
  cd backend
  alembic upgrade head
  ```

  **Expected:** All migrations apply successfully, all tables created

- [ ] **Verify all tables created**

  ```sql
  SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
  ```

  **Expected:** All 8 tables (including alembic_version) exist

- [ ] **Cleanup test database**
  ```bash
  docker exec ai-workflow-postgres psql -U postgres -c "DROP DATABASE ai_workflow_builder_test;"
  ```

### Documentation Verification

Check that database credentials, host, port, and connection settings are documented:

- [ ] **Check README.md**

  ```bash
  grep -i "postgres\|database" backend/README.md
  ```

  **Expected:** PostgreSQL setup instructions present

- [ ] **Check POSTGRES_SETUP.md exists**

  ```bash
  test -f backend/POSTGRES_SETUP.md && echo "File exists"
  ```

  **Expected:** Setup guide present

- [ ] **Verify documentation includes:**

  - [ ] Database connection string format
  - [ ] Default credentials (if applicable)
  - [ ] Host and port information
  - [ ] Setup instructions
  - [ ] Troubleshooting steps

- [ ] **Check Docker configuration documented**
  ```bash
  test -f backend/docker-compose.postgres.yml && echo "Docker compose exists"
  ```
  **Expected:** Docker setup documented

---

## 5. Data Backup / Fallback & Documentation

### SQLite Database Preservation

Optionally preserve the old SQLite database file as backup:

- [ ] **Locate SQLite database file**

  ```bash
  ls -lh backend/ai_workflow_builder.db
  ```

  **Expected:** File exists

- [ ] **Create backup copy**

  ```bash
  cp backend/ai_workflow_builder.db backend/ai_workflow_builder.db.backup_$(date +%Y%m%d)
  ```

  **Expected:** Backup created with date stamp

- [ ] **Document backup location**

  - Location: `backend/ai_workflow_builder.db.backup_YYYYMMDD`
  - Purpose: Archive of SQLite data before migration
  - Note: Label clearly to avoid accidental use

- [ ] **Update .gitignore** (if needed)
  ```bash
  echo "*.db.backup_*" >> backend/.gitignore
  ```
  **Expected:** Backup files not committed to repository

### Migration Documentation

Document that migration was done with date, commit hash, notes:

- [ ] **Create migration summary document**

  - Date: December 3, 2025
  - Migration method: Fresh PostgreSQL setup (no data migration from SQLite)
  - Database: PostgreSQL 16 (via Docker)
  - Connection: `postgresql+asyncpg://postgres:postgres@localhost:5432/ai_workflow_builder`

- [ ] **Document changes made:**

  - [ ] Config file updated: `backend/app/core/config.py`
  - [ ] Environment template created: `backend/.env.example`
  - [ ] Docker compose setup: `backend/docker-compose.postgres.yml`
  - [ ] Setup script created: `backend/scripts/setup_postgres.py`
  - [ ] Initial migration created: `backend/alembic/versions/20251203_2121_initial_migration_postgresql.py`
  - [ ] Migration applied successfully

- [ ] **Add migration notes to README**

  ```bash
  # Update backend/README.md with:
  # - PostgreSQL migration date
  # - Link to POSTGRES_SETUP.md
  # - Note about DATABASE_URL configuration
  ```

  **Expected:** README updated with migration information

- [ ] **Document SQLite file status**
  - File: `backend/ai_workflow_builder.db`
  - Status: Preserved for archival reference (optional backup)
  - Action: Can be archived or backed up before deletion
  - Location: Document backup location if moved

### PostgreSQL Backup Creation

Create a sample backup or dump of the new PostgreSQL database schema/data:

- [ ] **Create schema-only backup**

  ```bash
  docker exec ai-workflow-postgres pg_dump -U postgres -d ai_workflow_builder --schema-only > backend/backups/schema_backup_$(date +%Y%m%d).sql
  ```

  **Expected:** Schema backup created

- [ ] **Create full database backup** (optional, if data exists)

  ```bash
  docker exec ai-workflow-postgres pg_dump -U postgres -d ai_workflow_builder > backend/backups/full_backup_$(date +%Y%m%d).sql
  ```

  **Expected:** Full backup created (if needed)

- [ ] **Document backup location**

  - Location: `backend/backups/schema_backup_YYYYMMDD.sql`
  - Purpose: Clean baseline schema for future reference
  - Retention: Document retention policy

- [ ] **Test backup restoration** (optional)

  ```bash
  # Create test database
  docker exec ai-workflow-postgres psql -U postgres -c "CREATE DATABASE ai_workflow_builder_restore_test;"

  # Restore schema
  docker exec -i ai-workflow-postgres psql -U postgres -d ai_workflow_builder_restore_test < backend/backups/schema_backup_YYYYMMDD.sql

  # Verify tables created
  docker exec ai-workflow-postgres psql -U postgres -d ai_workflow_builder_restore_test -c "\dt"

  # Cleanup
  docker exec ai-workflow-postgres psql -U postgres -c "DROP DATABASE ai_workflow_builder_restore_test;"
  ```

  **Expected:** Backup can be restored successfully

---

## Quick Verification Commands

### Database Connection Test

```bash
cd backend
python scripts/setup_postgres.py
```

### Check Tables

```bash
docker exec ai-workflow-postgres psql -U postgres -d ai_workflow_builder -c "\dt"
```

### Check Migration Status

```bash
cd backend
alembic current
alembic history
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# API docs
# Open http://localhost:8000/docs in browser
```

### Run Tests

```bash
cd backend
pytest tests/ -v
```

---

## Migration Sign-Off

**Migration Status:** ☐ In Progress ☐ Complete ☐ Verified  
**Completed Date:** ******\_\_\_******  
**Verified By:** ******\_\_\_******  
**Notes/Issues:**

```
________________________________________________________________________
________________________________________________________________________
________________________________________________________________________
```

---

## Known Issues / Action Items

- [ ] Issue 1: ******\_\_\_******

  - Status: ******\_\_\_******
  - Resolution: ******\_\_\_******

- [ ] Issue 2: ******\_\_\_******
  - Status: ******\_\_\_******
  - Resolution: ******\_\_\_******

---

**Last Updated:** December 3, 2025  
**Next Review Date:** ******\_\_\_******
