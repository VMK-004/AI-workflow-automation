# AI Workflow Builder - Quick Start Guide

## 🚀 Get Up and Running in 5 Minutes

This guide will get you from zero to executing AI-powered workflows.

## Step 1: Setup (2 minutes)

```bash
# Clone/navigate to project
cd backend

# Install dependencies
pip install -r requirements.txt

# Setup database (PostgreSQL)
# Update .env with your database URL:
# DATABASE_URL=postgresql+asyncpg://user:password@localhost/workflow_db

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

Server now running at `http://localhost:8000`

## Step 2: Register & Login (1 minute)

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "email": "demo@example.com",
    "password": "demo123"
  }'

# Login (save the token!)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "password": "demo123"
  }'

# Set token
export TOKEN="<your_access_token_here>"
```

## Step 3: Create Your First Workflow (2 minutes)

### Create Workflow

```bash
curl -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First AI Workflow",
    "description": "LLM text generation workflow"
  }'

export WORKFLOW_ID="<your_workflow_id>"
```

### Add LLM Node

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "generate_text",
    "node_type": "llm_call",
    "config": {
      "prompt_template": "Write a short {style} paragraph about {topic}",
      "temperature": 0.8,
      "max_tokens": 150
    }
  }'
```

### Execute Workflow

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "topic": "space exploration",
      "style": "inspiring"
    }
  }'
```

**Note**: First execution loads the AI model (~10-30 seconds). Subsequent runs are much faster!

## Common Workflows

### 1. HTTP API Call

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "fetch_data",
    "node_type": "http_request",
    "config": {
      "url": "https://api.github.com/users/{username}",
      "method": "GET"
    }
  }'

# Execute
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"input_data": {"username": "octocat"}}'
```

### 2. Vector Search (after creating collection)

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "search_docs",
    "node_type": "faiss_search",
    "config": {
      "collection_name": "my_collection",
      "query": "{search_term}",
      "top_k": 3
    }
  }'
```

### 3. Database Write

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "save_result",
    "node_type": "db_write",
    "config": {
      "operation": "INSERT",
      "table": "results",
      "values": {
        "data": "{result}",
        "timestamp": "NOW()"
      }
    }
  }'
```

## Multi-Step Workflow

Create a chain: **LLM → HTTP → Database**

```bash
# Create 3 nodes
# Node 1: LLM
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "step1_generate",
    "node_type": "llm_call",
    "config": {
      "prompt_template": "Summarize: {text}",
      "max_tokens": 100
    }
  }'
NODE1="<id>"

# Node 2: HTTP
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "step2_post",
    "node_type": "http_request",
    "config": {
      "url": "https://webhook.site/your-id",
      "method": "POST",
      "body": {"summary": "{step1_generate_response}"}
    }
  }'
NODE2="<id>"

# Node 3: DB
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "step3_save",
    "node_type": "db_write",
    "config": {
      "operation": "INSERT",
      "table": "summaries",
      "values": {"text": "{step1_generate_response}"}
    }
  }'
NODE3="<id>"

# Connect them
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/edges \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"source_node_id\":\"$NODE1\",\"target_node_id\":\"$NODE2\"}"

curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/edges \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"source_node_id\":\"$NODE2\",\"target_node_id\":\"$NODE3\"}"

# Execute!
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"input_data": {"text": "Long article text here..."}}'
```

## View Execution Results

```bash
# Get run details
curl -X GET http://localhost:8000/api/workflows/$WORKFLOW_ID/runs/$RUN_ID \
  -H "Authorization: Bearer $TOKEN"
```

## Useful Endpoints

```bash
# List all workflows
curl -X GET http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $TOKEN"

# Get workflow details
curl -X GET http://localhost:8000/api/workflows/$WORKFLOW_ID \
  -H "Authorization: Bearer $TOKEN"

# List nodes
curl -X GET http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN"

# List edges
curl -X GET http://localhost:8000/api/workflows/$WORKFLOW_ID/edges \
  -H "Authorization: Bearer $TOKEN"
```

## Troubleshooting

### "Model not loaded"
The AI model loads on first use. Wait 10-30 seconds on first execution.

### "Collection not found"
Create FAISS collection first (see NODE_HANDLERS_TESTING.md).

### "Table doesn't exist"
Create database table before using db_write node.

### "Unauthorized"
Check your JWT token is set correctly: `echo $TOKEN`

## Next Steps

📖 **Read the docs**:
- `BACKEND_COMPLETE_STATUS.md` - Full feature list
- `NODE_HANDLERS_TESTING.md` - Detailed testing guide
- `EXECUTION_ENGINE_TESTING.md` - Advanced execution features

🎨 **Build the frontend**:
- Create React app
- Visual workflow editor
- Real-time monitoring

🚀 **Deploy to production**:
- Docker containerization
- Kubernetes deployment
- CI/CD pipeline

## Support

For more details, see the comprehensive documentation files in the project root.

---

**You're all set!** Start building AI-powered workflows! 🎉

