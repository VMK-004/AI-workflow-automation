# Backend Setup Guide

This guide will help you get the backend up and running.

## Quick Start

### 1. Install PostgreSQL

Make sure PostgreSQL is installed and running on your system.

### 2. Create Database

```sql
CREATE DATABASE workflow_db;
CREATE USER workflow_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE workflow_db TO workflow_user;
```

### 3. Setup Python Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env`:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edit `.env` and update these values:

```env
DATABASE_URL=postgresql+asyncpg://workflow_user:your_password@localhost:5432/workflow_db
SECRET_KEY=generate-a-secure-random-key-here
```

To generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Initialize Database

Option A - Using Alembic (recommended):

```bash
alembic upgrade head
```

Option B - Using init script:

```bash
python scripts/init_db.py
```

### 6. Create Test User (Optional)

```bash
python scripts/create_test_user.py
```

This creates:
- Username: `testuser`
- Password: `testpassword123`

### 7. Run Development Server

```bash
python -m app.main
```

Or with uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Test the API

Open your browser and visit:
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Project Structure

```
backend/
├── app/                    # Main application code
│   ├── api/               # API routes
│   ├── core/              # Configuration, security
│   ├── db/                # Database setup
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic (placeholder)
│   ├── node_handlers/     # Node execution handlers (placeholder)
│   └── utils/             # Utilities
├── alembic/               # Database migrations
├── data/                  # FAISS indexes storage
├── scripts/               # Helper scripts
└── tests/                 # Test files
```

## Next Steps

The backend skeleton is complete with:

✅ FastAPI app structure  
✅ SQLAlchemy async models (User, Workflow, Node, Edge, WorkflowRun, NodeExecution, VectorCollection)  
✅ Pydantic schemas for validation  
✅ API route placeholders (auth, workflows, nodes, edges, runs, vectors)  
✅ JWT authentication setup  
✅ Service layer structure (placeholder methods)  
✅ Node handler factory (placeholder handlers)  
✅ Alembic configuration  
✅ Testing setup  

### What to Implement Next:

1. **Authentication Logic** (`app/services/auth_service.py`, `app/api/routes/auth.py`)
   - User registration
   - Login with JWT token generation
   - Password validation

2. **Workflow CRUD** (`app/services/workflow_service.py`, `app/api/routes/workflows.py`)
   - Create/read/update/delete workflows
   - Node management
   - Edge management

3. **Execution Engine** (`app/services/execution_service.py`)
   - Graph loading
   - Topological sort
   - Node execution orchestration

4. **Node Handlers** (`app/node_handlers/`)
   - LLM call implementation
   - HTTP request handler
   - FAISS search handler
   - DB write handler

5. **LLM Service** (`app/services/llm_service.py`)
   - Load Qwen model
   - LangChain integration
   - Text generation

6. **Vector Service** (`app/services/vector_service.py`)
   - FAISS index creation
   - Document embedding
   - Similarity search

## Common Commands

```bash
# Run server
python -m app.main

# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check migration history
alembic history
```

## Troubleshooting

### Database Connection Error

Check:
1. PostgreSQL is running
2. Database exists
3. Credentials in `.env` are correct
4. Database URL format: `postgresql+asyncpg://user:password@host:port/database`

### Import Errors

Make sure:
1. Virtual environment is activated
2. All dependencies are installed: `pip install -r requirements.txt`
3. You're in the backend directory

### Alembic Migration Issues

Reset migrations:
```bash
# Drop all tables
python scripts/init_db.py

# Remove alembic versions
rm -rf alembic/versions/*.py  # Linux/Mac
del alembic\versions\*.py     # Windows

# Create fresh migration
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

