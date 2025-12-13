# AI Workflow Builder Platform

A full-stack agentic AI application for creating and executing AI-powered workflows with a graph-based node system.

## 🎯 Project Overview

AI Workflow Builder is a platform where users can:
- Create workflows as directed graphs of nodes and edges
- Define different node types (LLM calls, HTTP requests, vector search, database operations)
- Execute workflows end-to-end with automatic data flow between nodes
- View execution history and debug individual node outputs
- Store and search documents using FAISS vector database

## 🏗️ Architecture

### Technology Stack

**Backend:**
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL with async SQLAlchemy
- **AI/LLM:** LangChain + Qwen 0.5B/0.6B (local model)
- **Vector Store:** FAISS with sentence-transformers
- **Auth:** JWT tokens with bcrypt password hashing
- **Migrations:** Alembic

**Frontend:** (To be built)
- **Framework:** React with TypeScript
- **State:** Context API + custom hooks
- **HTTP Client:** Axios
- **Styling:** TBD (Tailwind CSS recommended)

### System Architecture

```
┌─────────────┐         ┌──────────────────────────────────────┐
│   React     │◄────────┤         FastAPI Backend              │
│  Frontend   │  HTTP   │                                      │
│ (TypeScript)│  +JWT   │  ┌────────────┐  ┌─────────────┐   │
└─────────────┘         │  │   Auth     │  │  Workflow   │   │
                        │  │  Service   │  │  Execution  │   │
                        │  └────────────┘  │   Engine    │   │
                        │                   └──────┬──────┘   │
                        │  ┌────────────┐         │          │
                        │  │   Node     │◄────────┘          │
                        │  │  Handlers  │                     │
                        │  └─────┬──────┘                     │
                        │        │                             │
                        │  ┌─────▼──────┐  ┌─────────────┐   │
                        │  │ LangChain  │  │   FAISS     │   │
                        │  │  + Qwen    │  │   Vector    │   │
                        │  │   0.6b     │  │   Store     │   │
                        │  └────────────┘  └─────────────┘   │
                        │                                      │
                        │  ┌────────────────────────────┐     │
                        │  │      PostgreSQL            │     │
                        │  └────────────────────────────┘     │
                        └──────────────────────────────────────┘
```

## 📁 Project Structure

```
AI Workflow Builder Platform/
├── ARCHITECTURE.md              # Detailed architecture documentation
├── README.md                    # This file
│
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── core/               # Config, security, dependencies
│   │   ├── db/                 # Database setup
│   │   ├── models/             # SQLAlchemy models (7 models)
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── api/routes/         # API endpoints (6 route modules)
│   │   ├── services/           # Business logic (6 services)
│   │   ├── node_handlers/      # Node type handlers (4 types)
│   │   └── utils/              # Utilities (graph, logger)
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Test suite
│   ├── requirements.txt        # Python dependencies
│   └── setup_and_run.md        # Setup instructions
│
└── frontend/                    # React frontend (to be built)
```

## 🚀 Quick Start

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Setup PostgreSQL:**
```sql
CREATE DATABASE ai_workflow_builder;
```

5. **Configure environment:**
```bash
# Copy .env.example and edit with your settings
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

6. **Run migrations:**
```bash
alembic upgrade head
```

7. **Start server:**
```bash
uvicorn app.main:app --reload
```

8. **Access API:**
- Main API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Setup

(To be implemented)

## 📊 Database Schema

### Core Tables

- **users** - User accounts with authentication
- **workflows** - Workflow definitions
- **nodes** - Individual workflow steps/nodes
- **edges** - Connections between nodes
- **workflow_runs** - Execution instances
- **node_executions** - Individual node execution logs
- **vector_collections** - FAISS index metadata

See `ARCHITECTURE.md` for detailed schema information.

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Workflows
- `GET /api/workflows` - List workflows
- `POST /api/workflows` - Create workflow
- `GET /api/workflows/{id}` - Get workflow
- `PUT /api/workflows/{id}` - Update workflow
- `DELETE /api/workflows/{id}` - Delete workflow

### Nodes
- `GET /api/workflows/{id}/nodes` - List nodes
- `POST /api/workflows/{id}/nodes` - Create node
- `GET /api/workflows/{id}/nodes/{node_id}` - Get node
- `PUT /api/workflows/{id}/nodes/{node_id}` - Update node
- `DELETE /api/workflows/{id}/nodes/{node_id}` - Delete node

### Edges
- `GET /api/workflows/{id}/edges` - List edges
- `POST /api/workflows/{id}/edges` - Create edge
- `DELETE /api/workflows/{id}/edges/{edge_id}` - Delete edge

### Workflow Execution
- `POST /api/workflows/{id}/runs` - Execute workflow
- `GET /api/workflows/{id}/runs` - List runs
- `GET /api/workflows/{id}/runs/{run_id}` - Get run details

### Vector Collections
- `GET /api/vectors/collections` - List collections
- `POST /api/vectors/collections` - Create collection
- `POST /api/vectors/collections/{name}/documents` - Add documents
- `POST /api/vectors/collections/{name}/search` - Search vectors
- `DELETE /api/vectors/collections/{name}` - Delete collection

## 🔧 Node Types

### 1. LLM Call (`llm_call`)
Execute Qwen LLM with custom prompts
```json
{
  "prompt_template": "Answer this: {input}",
  "temperature": 0.7,
  "max_tokens": 256
}
```

### 2. HTTP Request (`http_request`)
Make HTTP calls to external APIs
```json
{
  "method": "POST",
  "url": "https://api.example.com/endpoint",
  "headers": {},
  "body": {}
}
```

### 3. FAISS Search (`faiss_search`)
Semantic vector search
```json
{
  "collection_name": "documents",
  "query": "{input}",
  "top_k": 5
}
```

### 4. Database Write (`db_write`)
Write data to PostgreSQL
```json
{
  "table": "results",
  "data": {}
}
```

## 🏗️ Workflow Execution Engine

The execution engine:
1. Loads workflow graph from database
2. Performs topological sort for execution order
3. Executes nodes sequentially
4. Passes outputs between connected nodes
5. Logs all inputs/outputs for debugging
6. Handles errors and saves partial results

## 📝 Development Status

### ✅ Completed
- Complete backend folder structure
- All database models (7 models)
- All Pydantic schemas
- All API route skeletons (6 modules)
- Core services structure (6 services)
- Node handler framework (4 handlers)
- JWT authentication setup
- Alembic migration configuration
- Requirements and dependencies

### 🚧 In Progress
- Service implementation (business logic)
- Node handler implementations
- Execution engine core logic
- Frontend development

### 📋 Todo
- Implement authentication service
- Implement workflow CRUD operations
- Build execution engine with topological sort
- Implement node handlers (LLM, HTTP, FAISS, DB)
- Initialize Qwen model and LangChain integration
- Setup FAISS vector store
- Build React frontend
- Add tests for all components
- Add Docker configuration
- Add CI/CD pipeline

## 📖 Documentation

- **ARCHITECTURE.md** - Comprehensive architecture documentation
- **backend/README.md** - Backend-specific documentation
- **backend/setup_and_run.md** - Detailed setup instructions
- **backend/STRUCTURE.md** - File structure overview

## 🤝 Contributing

This is a personal project. Contributions are welcome!

## 📄 License

[To be decided]

## 🔗 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Qwen Models](https://huggingface.co/Qwen)

---

**Status:** Backend skeleton complete ✅ | Ready for implementation 🚀

# AI-workflow-automation




