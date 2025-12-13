# Node Handlers Testing Guide

## Quick Testing Workflow

This guide shows how to test each real node handler implementation.

## Prerequisites

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Start server:
```bash
uvicorn app.main:app --reload
```

3. Get authentication token (see AUTH_FLOW.md)

## Test 1: LLM Call Handler

### Step 1: Create Workflow

```bash
TOKEN="your_jwt_token"

# Create workflow
curl -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LLM Test Workflow",
    "description": "Test Qwen model integration"
  }'

WORKFLOW_ID="<save_workflow_id>"
```

### Step 2: Create LLM Node

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "generate_text",
    "node_type": "llm_call",
    "config": {
      "prompt_template": "Write a {length} paragraph about {topic}. Make it {style}.",
      "temperature": 0.8,
      "max_tokens": 200,
      "variables": {
        "style": "informative and engaging"
      }
    },
    "position_x": 100,
    "position_y": 100
  }'
```

### Step 3: Execute

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "topic": "artificial intelligence",
      "length": "short"
    }
  }'
```

**Expected Output:**
```json
{
  "workflow_run_id": "...",
  "status": "completed",
  "output": {
    "response": "Generated text about AI...",
    "model": "Qwen/Qwen-1_8B-Chat",
    "tokens_used": 350,
    "input_tokens": 100,
    "output_tokens": 250,
    "temperature": 0.8,
    "max_tokens": 200,
    "status": "success"
  },
  "node_outputs": {...}
}
```

**Note**: First execution will take 10-30 seconds to load the model. Subsequent runs will be faster.

## Test 2: HTTP Request Handler

### Create HTTP Node

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "fetch_data",
    "node_type": "http_request",
    "config": {
      "url": "https://jsonplaceholder.typicode.com/posts/{post_id}",
      "method": "GET",
      "timeout": 10
    },
    "position_x": 100,
    "position_y": 100
  }'
```

### Execute

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "post_id": "1"
    }
  }'
```

**Expected Output:**
```json
{
  "workflow_run_id": "...",
  "status": "completed",
  "output": {
    "status_code": 200,
    "headers": {...},
    "body": {
      "userId": 1,
      "id": 1,
      "title": "...",
      "body": "..."
    },
    "url": "https://jsonplaceholder.typicode.com/posts/1",
    "method": "GET",
    "elapsed_ms": 245.5,
    "status": "success"
  }
}
```

### Test POST Request

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_post",
    "node_type": "http_request",
    "config": {
      "url": "https://jsonplaceholder.typicode.com/posts",
      "method": "POST",
      "headers": {
        "Content-Type": "application/json"
      },
      "body": {
        "title": "{title}",
        "body": "{content}",
        "userId": 1
      }
    }
  }'

# Execute with data
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "title": "My Test Post",
      "content": "This is a test post created via workflow"
    }
  }'
```

## Test 3: FAISS Search Handler

### Step 1: Create FAISS Collection

First, create a test script to populate a FAISS collection:

```python
# create_faiss_collection.py
import asyncio
from app.services.vector_service import get_vector_service

async def create_test_collection():
    vector_service = get_vector_service()
    
    documents = [
        {
            "text": "Python is a high-level programming language known for its simplicity and readability.",
            "metadata": {"category": "programming", "language": "python"}
        },
        {
            "text": "FastAPI is a modern, fast web framework for building APIs with Python.",
            "metadata": {"category": "web", "framework": "fastapi"}
        },
        {
            "text": "Machine learning is a subset of artificial intelligence that enables computers to learn from data.",
            "metadata": {"category": "ai", "topic": "machine-learning"}
        },
        {
            "text": "Neural networks are computing systems inspired by biological neural networks in animal brains.",
            "metadata": {"category": "ai", "topic": "neural-networks"}
        },
        {
            "text": "PostgreSQL is a powerful, open-source relational database system.",
            "metadata": {"category": "database", "type": "sql"}
        },
        {
            "text": "FAISS is a library for efficient similarity search and clustering of dense vectors.",
            "metadata": {"category": "search", "library": "faiss"}
        },
    ]
    
    result = await vector_service.create_collection("tech_knowledge", documents)
    print(f"Collection created: {result}")

if __name__ == "__main__":
    asyncio.run(create_test_collection())
```

Run it:
```bash
cd backend
python create_faiss_collection.py
```

### Step 2: Create Search Node

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "search_knowledge",
    "node_type": "faiss_search",
    "config": {
      "collection_name": "tech_knowledge",
      "query": "What is {search_topic}?",
      "top_k": 3,
      "score_threshold": 0.3
    },
    "position_x": 100,
    "position_y": 100
  }'
```

### Step 3: Execute Search

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "search_topic": "artificial intelligence"
    }
  }'
```

**Expected Output:**
```json
{
  "workflow_run_id": "...",
  "status": "completed",
  "output": {
    "results": [
      {
        "text": "Machine learning is a subset of artificial intelligence...",
        "score": 0.87,
        "metadata": {"category": "ai", "topic": "machine-learning"}
      },
      {
        "text": "Neural networks are computing systems...",
        "score": 0.75,
        "metadata": {"category": "ai", "topic": "neural-networks"}
      },
      {
        "text": "FAISS is a library for efficient similarity search...",
        "score": 0.45,
        "metadata": {"category": "search", "library": "faiss"}
      }
    ],
    "query": "What is artificial intelligence?",
    "collection_name": "tech_knowledge",
    "total_results": 3,
    "top_k": 3,
    "score_threshold": 0.3,
    "status": "success"
  }
}
```

## Test 4: Database Write Handler

### Step 1: Create Test Table

```sql
-- Connect to your PostgreSQL database
CREATE TABLE execution_logs (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(255),
    message TEXT,
    log_level VARCHAR(50) DEFAULT 'INFO',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Step 2: Create DB Write Node (INSERT)

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "log_execution",
    "node_type": "db_write",
    "config": {
      "operation": "INSERT",
      "table": "execution_logs",
      "values": {
        "workflow_id": "{workflow_id}",
        "message": "{log_message}",
        "log_level": "INFO"
      },
      "returning": ["id", "created_at"]
    },
    "position_x": 100,
    "position_y": 100
  }'
```

### Step 3: Execute

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "workflow_id": "test-workflow-123",
      "log_message": "Workflow executed successfully"
    }
  }'
```

**Expected Output:**
```json
{
  "workflow_run_id": "...",
  "status": "completed",
  "output": {
    "operation": "INSERT",
    "table": "execution_logs",
    "rows_affected": 1,
    "returned": {
      "id": 1,
      "created_at": "2025-11-24T10:30:00"
    },
    "status": "success"
  }
}
```

### Test SELECT Query

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "fetch_logs",
    "node_type": "db_write",
    "config": {
      "operation": "SELECT",
      "table": "execution_logs",
      "columns": ["id", "workflow_id", "message", "created_at"],
      "where": {
        "workflow_id": "{workflow_id}"
      }
    }
  }'

# Execute
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "workflow_id": "test-workflow-123"
    }
  }'
```

### Test Raw SQL

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "custom_query",
    "node_type": "db_write",
    "config": {
      "raw_sql": "SELECT COUNT(*) as total FROM execution_logs WHERE log_level = :level",
      "params": {
        "level": "INFO"
      }
    }
  }'
```

## Test 5: Chained Workflow (All Handlers)

Create a workflow that chains all handlers together:

```
LLM (generate) → HTTP (send) → FAISS (search) → DB (log)
```

### Create Nodes

```bash
# Node 1: LLM
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "llm_generate",
    "node_type": "llm_call",
    "config": {
      "prompt_template": "Generate a summary about {topic}",
      "temperature": 0.7,
      "max_tokens": 100
    }
  }'
NODE1_ID="<save_id>"

# Node 2: HTTP
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "http_post",
    "node_type": "http_request",
    "config": {
      "url": "https://webhook.site/your-unique-id",
      "method": "POST",
      "body": {
        "summary": "{llm_generate_response}"
      }
    }
  }'
NODE2_ID="<save_id>"

# Node 3: FAISS
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "faiss_search",
    "node_type": "faiss_search",
    "config": {
      "collection_name": "tech_knowledge",
      "query": "{topic}",
      "top_k": 2
    }
  }'
NODE3_ID="<save_id>"

# Node 4: DB Write
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "db_log",
    "node_type": "db_write",
    "config": {
      "operation": "INSERT",
      "table": "execution_logs",
      "values": {
        "workflow_id": "{workflow_id}",
        "message": "Processed {topic} with {faiss_search_total_results} search results"
      }
    }
  }'
NODE4_ID="<save_id>"
```

### Create Edges

```bash
# Connect: LLM → HTTP
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/edges \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"source_node_id\":\"$NODE1_ID\",\"target_node_id\":\"$NODE2_ID\"}"

# Connect: HTTP → FAISS
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/edges \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"source_node_id\":\"$NODE2_ID\",\"target_node_id\":\"$NODE3_ID\"}"

# Connect: FAISS → DB
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/edges \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"source_node_id\":\"$NODE3_ID\",\"target_node_id\":\"$NODE4_ID\"}"
```

### Execute Chained Workflow

```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "topic": "machine learning",
      "workflow_id": "chained-test"
    }
  }'
```

You should see:
1. LLM generates text about machine learning
2. HTTP posts the summary to webhook.site
3. FAISS searches for related documents
4. DB logs the execution with search results count

## Troubleshooting

### LLM Handler Issues

**Problem**: Model fails to load
```
Solution: Check available disk space (~4GB needed) and memory (~8GB RAM recommended)
```

**Problem**: Generation is slow
```
Solution: Use GPU if available. Set device_map="cuda" in llm_service.py
```

### HTTP Handler Issues

**Problem**: SSL verification fails
```json
{
  "config": {
    "verify_ssl": false
  }
}
```

**Problem**: Request timeout
```json
{
  "config": {
    "timeout": 60
  }
}
```

### FAISS Handler Issues

**Problem**: Collection not found
```
Solution: Create collection first using create_faiss_collection.py script
```

**Problem**: Low quality results
```
Solution: Increase top_k or lower score_threshold
```

### DB Handler Issues

**Problem**: Table doesn't exist
```sql
-- Create table first
CREATE TABLE your_table (...);
```

**Problem**: Permission denied
```
Solution: Check database user has INSERT/UPDATE/DELETE permissions
```

## Monitoring Logs

Check server logs for detailed execution information:

```bash
# Server logs show:
# - Model loading progress
# - HTTP request details
# - Search queries and results
# - SQL queries executed
# - Error stack traces
```

## Next Steps

After testing all handlers:
1. Build complex multi-step workflows
2. Implement RAG (Retrieval-Augmented Generation) pipelines
3. Create data processing workflows
4. Build AI-powered automation chains

---

**Status**: All node handlers tested and working! 🎉





