# AI Workflow Builder - Architecture Plan

## 1. High Level System Architecture

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
                        │  │  (Users, Workflows, Runs)  │     │
                        │  └────────────────────────────┘     │
                        └──────────────────────────────────────┘
```

**Key Components:**

- **Frontend**: React app for workflow creation and management
- **Backend API**: FastAPI REST endpoints with JWT authentication
- **Execution Engine**: Graph-based workflow executor
- **Node Handlers**: Pluggable handlers for different node types
- **LangChain + Qwen**: LLM reasoning and tool orchestration
- **FAISS**: Vector search for semantic queries
- **PostgreSQL**: Persistent storage for all data

---

## 2. Backend Architecture

### Core Modules

```
backend/
├── app/
│   ├── core/           # Core configuration and utilities
│   ├── models/         # SQLAlchemy ORM models
│   ├── schemas/        # Pydantic schemas for validation
│   ├── api/            # API routes
│   ├── services/       # Business logic layer
│   ├── db/             # Database connection and session
│   └── auth/           # JWT authentication
```

### Architecture Layers

1. **API Layer** (`app/api/`): FastAPI routers for HTTP endpoints
2. **Service Layer** (`app/services/`): Business logic, workflow execution
3. **Data Layer** (`app/models/`): SQLAlchemy models for PostgreSQL
4. **Schema Layer** (`app/schemas/`): Request/response validation with Pydantic
5. **Core Layer** (`app/core/`): Configuration, dependencies, security

### Key Services

- **AuthService**: User registration, login, JWT token management
- **WorkflowService**: CRUD operations for workflows, nodes, edges
- **ExecutionService**: Core workflow execution engine
- **NodeHandlerService**: Factory pattern for node type handlers
- **VectorService**: FAISS vector store operations
- **LLMService**: Qwen model initialization and inference

---

## 3. Frontend Architecture

### Structure

```
frontend/
├── src/
│   ├── components/     # React components
│   ├── pages/          # Page-level components
│   ├── hooks/          # Custom React hooks
│   ├── services/       # API client services
│   ├── types/          # TypeScript type definitions
│   ├── context/        # React context for state management
│   └── utils/          # Helper functions
```

### Component Hierarchy

```
App
├── AuthProvider (Context)
├── Router
    ├── LoginPage
    ├── DashboardPage
    │   ├── WorkflowList
    │   └── CreateWorkflowButton
    ├── WorkflowDetailPage
    │   ├── NodeList
    │   ├── EdgeList
    │   ├── AddNodeForm
    │   └── RunWorkflowButton
    └── RunHistoryPage
        ├── RunList
        └── RunDetails
            └── NodeExecutionLogs
```

### State Management

- **AuthContext**: User authentication state, JWT token
- **WorkflowContext**: Current workflow, nodes, edges
- **Local State**: Component-specific state with useState/useReducer

---

## 4. Execution Engine Design

### Workflow Execution Flow

```
1. Load Workflow → 2. Build Graph → 3. Topological Sort → 4. Execute Nodes → 5. Save Results
```

### Detailed Steps

1. **Load Workflow Data**

   - Fetch workflow, nodes, edges from PostgreSQL
   - Create WorkflowRun record with status='running'

2. **Build Execution Graph**

   - Construct directed graph from nodes and edges
   - Validate graph (no cycles for now, DAG only)

3. **Determine Execution Order**

   - Perform topological sort
   - Identify parallel execution opportunities (future)

4. **Execute Nodes Sequentially**

   - For each node in order:
     - Get inputs from previous node outputs
     - Select appropriate node handler
     - Execute node logic
     - Store output and logs
     - Update node status (pending → running → completed/failed)

5. **Save Results**
   - Update WorkflowRun status
   - Store all node outputs and execution logs
   - Return execution summary

### Error Handling

- **Node Failure**: Mark node as failed, stop execution, log error
- **Retry Logic**: Optional retry count per node (future)
- **Partial Results**: Save all outputs up to failure point

### Context Passing

Each node receives:

```python
{
    "workflow_run_id": "uuid",
    "node_config": {...},
    "inputs": {
        "node_name_1": "output_value_1",
        "node_name_2": "output_value_2"
    },
    "global_context": {...}
}
```

---

## 5. Node Types and Handlers

### Node Type Interface

```python
class NodeHandler(ABC):
    @abstractmethod
    async def execute(self, config: dict, inputs: dict) -> dict:
        """Execute node logic and return output"""
        pass
```

### Supported Node Types

#### 1. **llm_call**

- **Purpose**: Call Qwen LLM with a prompt
- **Config**:
  ```json
  {
    "prompt_template": "Answer this: {input}",
    "temperature": 0.7,
    "max_tokens": 256
  }
  ```
- **Handler**: `LLMCallHandler` - Uses LangChain with Qwen model

#### 2. **http_request**

- **Purpose**: Make HTTP requests to external APIs
- **Config**:
  ```json
  {
    "method": "GET|POST|PUT|DELETE",
    "url": "https://api.example.com/endpoint",
    "headers": {...},
    "body": {...}
  }
  ```
- **Handler**: `HTTPRequestHandler` - Uses httpx async client

#### 3. **faiss_search**

- **Purpose**: Vector similarity search
- **Config**:
  ```json
  {
    "collection_name": "documents",
    "query": "{input}",
    "top_k": 5
  }
  ```
- **Handler**: `FAISSSearchHandler` - Queries FAISS index

#### 4. **db_write**

- **Purpose**: Write data to PostgreSQL (custom tables)
- **Config**:
  ```json
  {
    "table": "results",
    "data": {...}
  }
  ```
- **Handler**: `DBWriteHandler` - Direct database write

#### 5. **transform** (Future)

- **Purpose**: Transform data with Python expressions
- **Config**: `{"expression": "input.upper()"}`

#### 6. **condition** (Future)

- **Purpose**: Conditional branching
- **Config**: `{"condition": "input > 10"}`

### Node Handler Factory

```python
class NodeHandlerFactory:
    handlers = {
        "llm_call": LLMCallHandler,
        "http_request": HTTPRequestHandler,
        "faiss_search": FAISSSearchHandler,
        "db_write": DBWriteHandler
    }

    @staticmethod
    def get_handler(node_type: str) -> NodeHandler:
        return handlers[node_type]()
```

---

## 6. FAISS Integration Plan

### Vector Store Architecture

```
VectorService
├── create_collection(name, dimension)
├── add_documents(collection_name, texts, metadatas)
├── search(collection_name, query, top_k)
└── delete_collection(name)
```

### Storage Strategy

- **Index Files**: Store FAISS indexes on disk

  - Location: `data/faiss/{collection_name}.index`
  - Metadata: Store in PostgreSQL table `vector_collections`

- **Embedding Model**: Use sentence-transformers for embeddings
  - Model: `all-MiniLM-L6-v2` (384 dimensions, fast)
  - Alternative: Use Qwen embeddings (if available)

### FAISS Index Type

- **Start Simple**: `IndexFlatL2` (exact search, small datasets)
- **Scale Later**: `IndexIVFFlat` (approximate search, large datasets)

### Database Schema for Vectors

```sql
CREATE TABLE vector_collections (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    dimension INTEGER NOT NULL,
    index_path VARCHAR(512),
    document_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE vector_documents (
    id UUID PRIMARY KEY,
    collection_id UUID REFERENCES vector_collections(id),
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 7. Qwen Model Integration Plan

### Model Setup

- **Model**: Qwen2-0.5B-Instruct (or 0.6b if available)
- **Loading**: Load once at startup, keep in memory
- **Framework**: Use Hugging Face Transformers + LangChain integration

### LangChain Integration

```python
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# Initialize once
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
llm = HuggingFacePipeline(pipeline=pipe)
```

### LLM Service

```python
class LLMService:
    def __init__(self):
        self.llm = self._load_model()

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        return await self.llm.ainvoke(prompt)

    async def generate_with_tools(self, prompt: str, tools: list) -> str:
        """Use LLM with LangChain tools"""
        agent = create_react_agent(self.llm, tools)
        return await agent.ainvoke(prompt)
```

### Model Configuration

- **Temperature**: 0.7 (default, configurable per node)
- **Max Tokens**: 256 (default, configurable)
- **Device**: CPU (small model, acceptable latency)
- **Batch Size**: 1 (process nodes sequentially)

### Future Enhancements

- GPU support (CUDA)
- Model caching for repeated prompts
- Streaming responses
- Multiple model support

---

## 8. PostgreSQL Schema Overview

### Entity Relationship

```
users
  ↓ (1:N)
workflows
  ↓ (1:N)
nodes, edges
  ↓ (1:N)
workflow_runs
  ↓ (1:N)
node_executions
```

### Table Definitions

#### **users**

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### **workflows**

```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### **nodes**

```sql
CREATE TABLE nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    node_type VARCHAR(50) NOT NULL, -- llm_call, http_request, etc.
    config JSONB NOT NULL, -- Node-specific configuration
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(workflow_id, name)
);
```

#### **edges**

```sql
CREATE TABLE edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
    source_node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    target_node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_node_id, target_node_id)
);
```

#### **workflow_runs**

```sql
CREATE TABLE workflow_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT,
    input_data JSONB,
    output_data JSONB
);
```

#### **node_executions**

```sql
CREATE TABLE node_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_run_id UUID REFERENCES workflow_runs(id) ON DELETE CASCADE,
    node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    execution_order INTEGER
);
```

#### **vector_collections**

```sql
CREATE TABLE vector_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    dimension INTEGER NOT NULL,
    index_path VARCHAR(512),
    document_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, name)
);
```

### Indexes

```sql
CREATE INDEX idx_workflows_user_id ON workflows(user_id);
CREATE INDEX idx_nodes_workflow_id ON nodes(workflow_id);
CREATE INDEX idx_edges_workflow_id ON edges(workflow_id);
CREATE INDEX idx_workflow_runs_workflow_id ON workflow_runs(workflow_id);
CREATE INDEX idx_workflow_runs_user_id ON workflow_runs(user_id);
CREATE INDEX idx_node_executions_run_id ON node_executions(workflow_run_id);
CREATE INDEX idx_vector_collections_user_id ON vector_collections(user_id);
```

---

## 9. API Route Map

### Authentication (`/api/auth`)

- `POST /api/auth/register` - Register new user

  - Request: `{username, email, password}`
  - Response: `{id, username, email, access_token}`

- `POST /api/auth/login` - Login user

  - Request: `{username, password}`
  - Response: `{access_token, token_type}`

- `GET /api/auth/me` - Get current user (protected)
  - Response: `{id, username, email}`

### Workflows (`/api/workflows`)

- `GET /api/workflows` - List user workflows
- `POST /api/workflows` - Create workflow
  - Request: `{name, description}`
- `GET /api/workflows/{workflow_id}` - Get workflow details
- `PUT /api/workflows/{workflow_id}` - Update workflow
- `DELETE /api/workflows/{workflow_id}` - Delete workflow

### Nodes (`/api/workflows/{workflow_id}/nodes`)

- `GET /api/workflows/{workflow_id}/nodes` - List nodes
- `POST /api/workflows/{workflow_id}/nodes` - Create node
  - Request: `{name, node_type, config, position_x, position_y}`
- `GET /api/workflows/{workflow_id}/nodes/{node_id}` - Get node
- `PUT /api/workflows/{workflow_id}/nodes/{node_id}` - Update node
- `DELETE /api/workflows/{workflow_id}/nodes/{node_id}` - Delete node

### Edges (`/api/workflows/{workflow_id}/edges`)

- `GET /api/workflows/{workflow_id}/edges` - List edges
- `POST /api/workflows/{workflow_id}/edges` - Create edge
  - Request: `{source_node_id, target_node_id}`
- `DELETE /api/workflows/{workflow_id}/edges/{edge_id}` - Delete edge

### Workflow Execution (`/api/workflows/{workflow_id}/runs`)

- `POST /api/workflows/{workflow_id}/runs` - Execute workflow
  - Request: `{input_data: {...}}`
  - Response: `{run_id, status}`
- `GET /api/workflows/{workflow_id}/runs` - List runs
- `GET /api/workflows/{workflow_id}/runs/{run_id}` - Get run details
  - Response: `{run, node_executions: [...]}`

### Vector Collections (`/api/vectors`)

- `GET /api/vectors/collections` - List collections
- `POST /api/vectors/collections` - Create collection
  - Request: `{name, dimension}`
- `POST /api/vectors/collections/{name}/documents` - Add documents
  - Request: `{texts: [], metadatas: []}`
- `POST /api/vectors/collections/{name}/search` - Search vectors
  - Request: `{query, top_k}`
- `DELETE /api/vectors/collections/{name}` - Delete collection

---

## 10. Full Folder Structure

### Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Settings (env vars, DB URL)
│   │   ├── security.py            # JWT, password hashing
│   │   └── dependencies.py        # FastAPI dependencies
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py            # SQLAlchemy engine, session
│   │   └── base.py                # Base model for all tables
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                # User model
│   │   ├── workflow.py            # Workflow model
│   │   ├── node.py                # Node model
│   │   ├── edge.py                # Edge model
│   │   ├── workflow_run.py        # WorkflowRun model
│   │   ├── node_execution.py      # NodeExecution model
│   │   └── vector_collection.py   # VectorCollection model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                # User schemas (request/response)
│   │   ├── workflow.py            # Workflow schemas
│   │   ├── node.py                # Node schemas
│   │   ├── edge.py                # Edge schemas
│   │   ├── workflow_run.py        # WorkflowRun schemas
│   │   └── vector.py              # Vector schemas
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # Auth endpoints
│   │   │   ├── workflows.py       # Workflow endpoints
│   │   │   ├── nodes.py           # Node endpoints
│   │   │   ├── edges.py           # Edge endpoints
│   │   │   ├── runs.py            # Workflow run endpoints
│   │   │   └── vectors.py         # Vector endpoints
│   │   └── deps.py                # Route dependencies (auth, db)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py        # Authentication logic
│   │   ├── workflow_service.py    # Workflow CRUD
│   │   ├── execution_service.py   # Workflow execution engine
│   │   ├── node_handler_service.py # Node handler factory
│   │   ├── llm_service.py         # Qwen LLM service
│   │   └── vector_service.py      # FAISS vector store
│   │
│   ├── node_handlers/
│   │   ├── __init__.py
│   │   ├── base.py                # NodeHandler abstract class
│   │   ├── llm_call.py            # LLM call handler
│   │   ├── http_request.py        # HTTP request handler
│   │   ├── faiss_search.py        # FAISS search handler
│   │   └── db_write.py            # DB write handler
│   │
│   └── utils/
│       ├── __init__.py
│       ├── graph.py               # Graph utilities (topological sort)
│       └── logger.py              # Logging configuration
│
├── alembic/                       # Database migrations
│   ├── versions/
│   └── env.py
│
├── data/
│   └── faiss/                     # FAISS index storage
│
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_workflows.py
│   └── test_execution.py
│
├── .env                           # Environment variables
├── .env.example
├── requirements.txt               # Python dependencies
├── alembic.ini                    # Alembic config
└── README.md
```

### Frontend Structure

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
│
├── src/
│   ├── App.tsx                    # Main app component
│   ├── index.tsx                  # Entry point
│   ├── index.css                  # Global styles
│   │
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   │
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   │
│   │   ├── workflows/
│   │   │   ├── WorkflowList.tsx
│   │   │   ├── WorkflowCard.tsx
│   │   │   ├── CreateWorkflowModal.tsx
│   │   │   └── WorkflowDetail.tsx
│   │   │
│   │   ├── nodes/
│   │   │   ├── NodeList.tsx
│   │   │   ├── NodeCard.tsx
│   │   │   ├── CreateNodeModal.tsx
│   │   │   └── NodeConfigForm.tsx
│   │   │
│   │   ├── edges/
│   │   │   ├── EdgeList.tsx
│   │   │   └── CreateEdgeModal.tsx
│   │   │
│   │   └── runs/
│   │       ├── RunList.tsx
│   │       ├── RunCard.tsx
│   │       ├── RunDetails.tsx
│   │       └── NodeExecutionLog.tsx
│   │
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── WorkflowDetailPage.tsx
│   │   └── RunHistoryPage.tsx
│   │
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useWorkflows.ts
│   │   ├── useNodes.ts
│   │   └── useRuns.ts
│   │
│   ├── services/
│   │   ├── api.ts                 # Axios instance, interceptors
│   │   ├── authService.ts         # Auth API calls
│   │   ├── workflowService.ts     # Workflow API calls
│   │   ├── nodeService.ts         # Node API calls
│   │   ├── edgeService.ts         # Edge API calls
│   │   └── runService.ts          # Run API calls
│   │
│   ├── context/
│   │   ├── AuthContext.tsx        # Auth state provider
│   │   └── WorkflowContext.tsx    # Workflow state provider
│   │
│   ├── types/
│   │   ├── index.ts               # Export all types
│   │   ├── auth.ts
│   │   ├── workflow.ts
│   │   ├── node.ts
│   │   └── run.ts
│   │
│   └── utils/
│       ├── constants.ts
│       └── helpers.ts
│
├── .env                           # Environment variables
├── .env.example
├── package.json
├── tsconfig.json
├── tailwind.config.js             # (Optional) Tailwind CSS
└── README.md
```

---

## 11. Scalability & Best Practices

### Backend

1. **Async Everywhere**

   - Use `async def` for all I/O operations
   - Use `asyncpg` for PostgreSQL (or SQLAlchemy async)
   - Use `httpx` for HTTP requests

2. **Connection Pooling**

   - PostgreSQL connection pool (SQLAlchemy handles this)
   - Reuse FAISS indexes (load once, keep in memory)
   - Reuse Qwen model (singleton pattern)

3. **Error Handling**

   - Custom exception classes
   - Global exception handlers in FastAPI
   - Structured logging with context

4. **Security**

   - JWT with expiration (15-60 min)
   - Password hashing with bcrypt
   - Rate limiting (future: use slowapi)
   - Input validation with Pydantic

5. **Testing**

   - Unit tests for services
   - Integration tests for API routes
   - Mock external dependencies (LLM, HTTP)

6. **Performance**
   - Index database columns (user_id, workflow_id)
   - Use JSONB for node config (queryable)
   - Cache workflow graphs (future: Redis)
   - Background tasks for long executions (Celery future)

### Frontend

1. **Code Organization**

   - One component per file
   - Colocate related components
   - Extract reusable logic to hooks

2. **State Management**

   - Context for global state (auth)
   - Local state for UI components
   - React Query for server state (future)

3. **API Calls**

   - Centralize API client (axios instance)
   - Add auth token interceptor
   - Handle errors globally

4. **Type Safety**

   - Define types for all API responses
   - Use strict TypeScript mode
   - Avoid `any` type

5. **Performance**

   - Lazy load routes (React.lazy)
   - Memoize expensive components
   - Debounce search inputs

6. **UX**
   - Loading states for async operations
   - Error messages for failed requests
   - Optimistic updates where possible

### Execution Engine

1. **Graph Validation**

   - Check for cycles (DAG only for now)
   - Verify all nodes have handlers
   - Validate node configurations

2. **Execution Strategy**

   - Start with sequential execution
   - Future: Parallel execution for independent nodes
   - Future: Conditional branching

3. **Error Recovery**

   - Save partial results on failure
   - Add retry logic per node
   - Allow resuming failed runs (future)

4. **Monitoring**
   - Log execution time per node
   - Track memory usage
   - Alert on failures

### Database

1. **Migrations**

   - Use Alembic for schema changes
   - Version control all migrations
   - Test migrations on staging first

2. **Optimization**

   - Add indexes on foreign keys
   - Use JSONB for flexible schemas
   - Regular VACUUM ANALYZE

3. **Backup**
   - Daily automated backups
   - Point-in-time recovery enabled
   - Test restore procedures

### Deployment (Future)

1. **Containerization**

   - Dockerfile for backend
   - Dockerfile for frontend (nginx)
   - Docker Compose for local dev

2. **Environment Management**

   - Separate configs for dev/staging/prod
   - Use environment variables
   - Never commit secrets

3. **Monitoring**
   - Health check endpoints
   - Application metrics (Prometheus)
   - Log aggregation (ELK stack)

---

## Summary

This architecture provides:

- **Modularity**: Clear separation of concerns
- **Scalability**: Async operations, connection pooling
- **Maintainability**: Organized folder structure, typed code
- **Extensibility**: Easy to add new node types
- **Clarity**: Straightforward execution flow

Next steps: Implement backend skeleton → execution engine → node handlers → frontend → integration testing.
