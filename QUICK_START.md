# Quick Start Guide

## Backend Setup (5 Minutes)

### 1. Install Dependencies
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 2. Setup Database
```sql
-- In PostgreSQL
CREATE DATABASE ai_workflow_builder;
```

### 3. Configure Environment
```bash
# Create .env file in backend/
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ai_workflow_builder
SECRET_KEY=your-secret-key-change-me
DEBUG=True
```

### 4. Run Migrations
```bash
# In backend/
alembic revision --autogenerate -m "initial_migration"
alembic upgrade head
```

### 5. Start Server
```bash
uvicorn app.main:app --reload
```

### 6. Test It
Visit http://localhost:8000/docs for interactive API documentation!

## File Reference

### Need to implement user registration?
→ `backend/app/services/auth_service.py`

### Need to add workflow CRUD logic?
→ `backend/app/services/workflow_service.py`

### Need to build execution engine?
→ `backend/app/services/execution_service.py`

### Need to add graph algorithms?
→ `backend/app/utils/graph.py`

### Need to implement a node handler?
→ `backend/app/node_handlers/llm_call.py` (or others)

### Need to configure the app?
→ `backend/app/core/config.py`

### Need to add a new API endpoint?
→ `backend/app/api/routes/` (choose appropriate module)

### Need to add a database model?
→ `backend/app/models/` + update `backend/app/db/base.py`

## Common Commands

```bash
# Start development server
uvicorn app.main:app --reload

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Run tests
pytest

# Check code style
flake8 app/

# Type checking
mypy app/
```

## API Testing Examples

### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"password123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"password123"}'
```

### Create Workflow (with token)
```bash
curl -X POST http://localhost:8000/api/workflows \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"name":"My First Workflow","description":"Test workflow"}'
```

## Directory Navigation

```
backend/
├── app/
│   ├── main.py              ← Start here (FastAPI app)
│   ├── core/                ← Config & security
│   ├── models/              ← Database tables (7 models)
│   ├── schemas/             ← Request/response validation
│   ├── api/routes/          ← API endpoints (24 endpoints)
│   ├── services/            ← Business logic (implement here!)
│   ├── node_handlers/       ← Node type logic (implement here!)
│   └── utils/               ← Helper functions
└── alembic/                 ← Database migrations
```

## What to Implement First?

### Priority 1: Basic Auth & Workflows
1. `auth_service.py` → Register and login users
2. `workflow_service.py` → Create/read/update/delete workflows
3. Test with Swagger UI at /docs

### Priority 2: Execution Engine
1. `graph.py` → Topological sort
2. `execution_service.py` → Execute workflow
3. `llm_call.py` → Implement LLM node

### Priority 3: Advanced Features
1. `llm_service.py` → Load Qwen model
2. `vector_service.py` → FAISS operations
3. Other node handlers

## Troubleshooting

### Import Errors
Make sure you're in the `backend/` directory and venv is activated.

### Database Errors
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure database exists

### Alembic Errors
- Make sure all models are imported in `app/db/base.py`
- Check `alembic.ini` has correct config
- Run from `backend/` directory

### Module Not Found
```bash
pip install -r requirements.txt
```

## Need Help?

1. Check `ARCHITECTURE.md` for system design
2. Check `BACKEND_COMPLETE.md` for what's built
3. Check `backend/README.md` for backend docs
4. Use `/docs` endpoint for API reference

---

**You're all set! Start coding! 🚀**





