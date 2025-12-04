# Backend Directory Structure

```
backend/
├── alembic/                      # Database migrations
│   ├── env.py                    # Alembic environment config
│   ├── script.py.mako            # Migration template
│   └── versions/                 # Migration files (created after first migration)
│
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI app initialization & routes setup
│   │
│   ├── core/                     # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py             # Settings from environment variables
│   │   ├── security.py           # JWT & password hashing utilities
│   │   └── dependencies.py       # FastAPI dependencies (auth, db)
│   │
│   ├── db/                       # Database configuration
│   │   ├── __init__.py
│   │   ├── database.py           # SQLAlchemy async engine & session
│   │   └── base.py               # Import all models for Alembic
│   │
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py               # User model
│   │   ├── workflow.py           # Workflow model
│   │   ├── node.py               # Node model
│   │   ├── edge.py               # Edge model
│   │   ├── workflow_run.py       # WorkflowRun model
│   │   ├── node_execution.py     # NodeExecution model
│   │   └── vector_collection.py  # VectorCollection model
│   │
│   ├── schemas/                  # Pydantic schemas (validation)
│   │   ├── __init__.py
│   │   ├── user.py               # User request/response schemas
│   │   ├── workflow.py           # Workflow schemas
│   │   ├── node.py               # Node schemas
│   │   ├── edge.py               # Edge schemas
│   │   ├── workflow_run.py       # WorkflowRun schemas
│   │   └── vector.py             # Vector collection schemas
│   │
│   ├── api/                      # API routes
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py           # Authentication endpoints
│   │       ├── workflows.py      # Workflow CRUD endpoints
│   │       ├── nodes.py          # Node CRUD endpoints
│   │       ├── edges.py          # Edge CRUD endpoints
│   │       ├── runs.py           # Workflow execution endpoints
│   │       └── vectors.py        # Vector collection endpoints
│   │
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py       # User authentication logic
│   │   ├── workflow_service.py   # Workflow CRUD operations
│   │   ├── execution_service.py  # Workflow execution engine
│   │   ├── llm_service.py        # Qwen LLM integration
│   │   ├── vector_service.py     # FAISS vector operations
│   │   └── node_handler_service.py # Node handler factory
│   │
│   ├── node_handlers/            # Node type implementations
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract NodeHandler class
│   │   ├── llm_call.py           # LLM call handler
│   │   ├── http_request.py       # HTTP request handler
│   │   ├── faiss_search.py       # FAISS search handler
│   │   └── db_write.py           # Database write handler
│   │
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       ├── graph.py              # Graph algorithms (topological sort)
│       └── logger.py             # Logging configuration
│
├── data/                         # Data storage
│   └── faiss/                    # FAISS index files
│       └── .gitkeep
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_auth.py              # Authentication tests
│   ├── test_workflows.py         # Workflow tests
│   └── test_execution.py         # Execution engine tests
│
├── .env.example                  # Example environment variables
├── .gitignore                    # Git ignore file
├── alembic.ini                   # Alembic configuration
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
├── setup_and_run.md              # Setup instructions
└── STRUCTURE.md                  # This file
```

## File Count Summary

- **7 Models** (User, Workflow, Node, Edge, WorkflowRun, NodeExecution, VectorCollection)
- **6 Schema modules** (user, workflow, node, edge, workflow_run, vector)
- **6 API route modules** (auth, workflows, nodes, edges, runs, vectors)
- **6 Services** (auth, workflow, execution, llm, vector, node_handler)
- **4 Node handlers** (llm_call, http_request, faiss_search, db_write)
- **3 Core modules** (config, security, dependencies)
- **3 Test files** (auth, workflows, execution)

**Total: 56 Python files + configuration files**

## Next Steps

1. Set up virtual environment and install dependencies
2. Configure PostgreSQL database
3. Set up .env file with credentials
4. Run Alembic migrations
5. Start implementing service logic
6. Test API endpoints

See `setup_and_run.md` for detailed setup instructions.


