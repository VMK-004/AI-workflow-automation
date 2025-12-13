# 🤖 AI Workflow Builder Platform

<div align="center">

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-009688.svg)
![React](https://img.shields.io/badge/react-19.2.0-61DAFB.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.9.3-3178C6.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-15+-336791.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**A full-stack platform for creating and executing AI-powered workflows with a visual graph-based editor**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [API Reference](#-api-reference) • [Deployment](#-deployment)

[🌐 Live Demo](https://ai-workflow-automation-ikld.onrender.com) • [📖 Documentation](./ARCHITECTURE.md) • [🐛 Report Bug](https://github.com/VMK-004/AI-workflow-automation/issues)

</div>

---

## ✨ Features

### 🎯 Core Capabilities

- **🔄 Visual Workflow Builder** - Create complex workflows using a drag-and-drop graph interface
- **🧠 AI-Powered Nodes** - Integrate LLM calls using Qwen models via LangChain
- **🔍 Semantic Search** - FAISS vector search with sentence-transformers for RAG applications
- **🌐 API Integration** - Make HTTP requests to external services and APIs
- **💾 Database Operations** - Execute SQL queries and write results to PostgreSQL
- **📊 Execution Tracking** - Monitor workflow runs with detailed logs and debugging
- **🔐 Secure Authentication** - JWT-based auth with bcrypt password hashing
- **👥 Multi-User Support** - User-scoped workflows and data isolation

### 🎨 Node Types

| Node Type | Description | Use Cases |
|-----------|-------------|-----------|
| **LLM Call** | Execute Qwen LLM with custom prompts | Text generation, summarization, Q&A |
| **HTTP Request** | Make REST API calls | External service integration |
| **FAISS Search** | Semantic vector similarity search | RAG, document retrieval, similarity matching |
| **DB Write** | Write data to PostgreSQL | Logging, result storage, data persistence |

### 🚀 Key Highlights

- ✅ **Production Ready** - Fully deployed on Render.com
- ✅ **Full-Stack** - React frontend + FastAPI backend
- ✅ **Async Architecture** - High-performance async/await throughout
- ✅ **Type-Safe** - TypeScript frontend + Pydantic backend validation
- ✅ **Graph Validation** - Automatic cycle detection and topological sorting
- ✅ **Vector Collections** - Upload documents, create embeddings, semantic search

---

## 🏗️ Architecture

### Technology Stack

**Backend:**
- 🐍 **FastAPI** - Modern Python web framework
- 🗄️ **PostgreSQL** - Relational database with async SQLAlchemy
- 🤖 **LangChain** - LLM orchestration framework
- 🔤 **Qwen 0.6B** - Lightweight local LLM (via Ollama)
- 🔍 **FAISS** - Vector similarity search
- 🔐 **JWT + bcrypt** - Authentication & security
- 📦 **Alembic** - Database migrations

**Frontend:**
- ⚛️ **React 19** - UI library
- 📘 **TypeScript** - Type safety
- 🎨 **Tailwind CSS** - Utility-first styling
- 🔄 **Zustand** - State management
- 📡 **Axios** - HTTP client
- 🗺️ **React Router** - Client-side routing

### System Architecture

```
┌─────────────────┐         ┌──────────────────────────────────────┐
│   React + TS    │◄────────┤      FastAPI Backend                 │
│   Frontend      │  HTTP   │                                      │
│  (Tailwind)     │  +JWT   │  ┌────────────┐  ┌─────────────┐   │
└─────────────────┘         │  │   Auth     │  │  Workflow   │   │
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
                            │  │  (7 tables, async ORM)     │     │
                            │  └────────────────────────────┘     │
                            └──────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 15+
- Docker (optional, for containerized deployment)

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/VMK-004/AI-workflow-automation.git
cd AI-workflow-automation
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL database
createdb ai_workflow_builder  # Or use psql to create manually

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# VITE_API_URL=http://localhost:8000/api

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

---

## 📊 Database Schema

The platform uses 7 core database tables:

| Table | Description |
|-------|-------------|
| `users` | User accounts with authentication |
| `workflows` | Workflow definitions |
| `nodes` | Individual workflow steps/nodes |
| `edges` | Connections between nodes |
| `workflow_runs` | Execution instances |
| `node_executions` | Individual node execution logs |
| `vector_collections` | FAISS index metadata |

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed schema information.

---

## 🔌 API Reference

### Authentication

```http
POST /api/auth/register     # Register new user
POST /api/auth/login        # Login and get JWT token
GET  /api/auth/me           # Get current user info
```

### Workflows

```http
GET    /api/workflows              # List workflows
POST   /api/workflows              # Create workflow
GET    /api/workflows/{id}         # Get workflow
PUT    /api/workflows/{id}         # Update workflow
DELETE /api/workflows/{id}         # Delete workflow
POST   /api/workflows/{id}/execute # Execute workflow
GET    /api/workflows/{id}/runs    # List execution runs
```

### Nodes & Edges

```http
GET    /api/workflows/{id}/nodes     # List nodes
POST   /api/workflows/{id}/nodes     # Create node
PUT    /api/workflows/{id}/nodes/{node_id}  # Update node
DELETE /api/workflows/{id}/nodes/{node_id}  # Delete node

GET    /api/workflows/{id}/edges     # List edges
POST   /api/workflows/{id}/edges     # Create edge
DELETE /api/workflows/{id}/edges/{edge_id}  # Delete edge
```

### Vector Collections

```http
GET    /api/vectors/collections                    # List collections
POST   /api/vectors/collections                    # Create collection
POST   /api/vectors/collections/{name}/documents   # Add documents
POST   /api/vectors/collections/{name}/search      # Semantic search
POST   /api/vectors/collections/{name}/upload      # Upload files (PDF, DOCX, TXT)
DELETE /api/vectors/collections/{name}             # Delete collection
```

**📖 Full API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

---

## 🐳 Deployment

### Render.com (Current Deployment)

The application is currently deployed on Render.com:
- **Live URL**: https://ai-workflow-automation-ikld.onrender.com
- **Frontend + Backend**: Combined in single Docker container
- **Database**: Render PostgreSQL
- **Auto-deploy**: Enabled on git push

### Docker Deployment

```bash
# Build and run
docker build -t ai-workflow-builder .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host/db \
  -e SECRET_KEY=your-secret-key \
  ai-workflow-builder
```

See [RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

---

## 📝 Example Workflows

### RAG Pipeline (Retrieval Augmented Generation)

```
User Query
    ↓
FAISS Search (retrieve relevant documents)
    ↓
LLM Call (generate answer with context)
    ↓
HTTP Post (send to external API)
    ↓
DB Write (log interaction)
```

### Data Processing Pipeline

```
HTTP Fetch Data
    ↓
LLM Extract Information
    ↓
DB Write Results
    ↓
FAISS Index for Future Search
```

---

## 🧪 Testing

### Manual API Testing

All endpoints can be tested using the interactive Swagger UI:
- Visit `http://localhost:8000/docs` when running locally
- Or visit `https://ai-workflow-automation-ikld.onrender.com/docs` for production

### Example: Create and Execute a Workflow

```bash
# 1. Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123"}'

# 2. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# 3. Create workflow
curl -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Workflow","description":"Test workflow"}'

# 4. Execute workflow
curl -X POST http://localhost:8000/api/workflows/{workflow_id}/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"input_data":{"query":"Hello"}}'
```

---

## 📖 Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Comprehensive system architecture
- **[RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md)** - Production deployment guide
- **[backend/README.md](./backend/README.md)** - Backend-specific documentation
- **[backend/SETUP_GUIDE.md](./backend/SETUP_GUIDE.md)** - Detailed setup instructions
- **[frontend/README.md](./frontend/README.md)** - Frontend documentation

---

## 🛠️ Development Status

### ✅ Completed Features

- ✅ Full-stack application (Frontend + Backend)
- ✅ User authentication & authorization
- ✅ Workflow CRUD operations
- ✅ Node management (4 types)
- ✅ Edge management (graph connections)
- ✅ Graph validation (cycles, topology)
- ✅ Workflow execution engine
- ✅ Real node handlers (LLM, HTTP, FAISS, DB)
- ✅ Vector collections API
- ✅ File upload & parsing (PDF, DOCX, TXT)
- ✅ Production deployment
- ✅ Automatic database migrations

### 🚧 Roadmap

- [ ] Unit and integration tests
- [ ] Workflow templates
- [ ] Conditional branching nodes
- [ ] Parallel execution
- [ ] Scheduled workflows
- [ ] Webhook triggers
- [ ] Advanced visual editor enhancements

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [LangChain](https://www.langchain.com/) - LLM orchestration framework
- [FAISS](https://github.com/facebookresearch/faiss) - Vector similarity search
- [React](https://react.dev/) - UI library
- [Qwen](https://huggingface.co/Qwen) - Lightweight LLM models

---

## 📧 Contact

- **GitHub**: [@VMK-004](https://github.com/VMK-004)
- **Repository**: [AI-workflow-automation](https://github.com/VMK-004/AI-workflow-automation)
- **Live Demo**: [ai-workflow-automation.onrender.com](https://ai-workflow-automation-ikld.onrender.com)

---

<div align="center">

**Made with ❤️ using FastAPI, React, and LangChain**

⭐ Star this repo if you find it useful!

</div>