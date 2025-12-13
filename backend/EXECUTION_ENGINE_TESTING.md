# Execution Engine Testing Guide

## Overview

The execution engine is now fully implemented and ready to execute workflows. This guide shows how to test the workflow execution functionality.

## Architecture

### Services

1. **ExecutionService** (`app/services/execution_service.py`)
   - Core workflow execution engine
   - Orchestrates the entire execution process
   - Methods:
     - `execute_workflow()` - Main execution entry point
     - `_execute_nodes()` - Execute all nodes in order
     - `_execute_single_node()` - Execute one node
     - `get_workflow_run_details()` - Get run information

2. **WorkflowRunService** (`app/services/workflow_run_service.py`)
   - Manages WorkflowRun records
   - Methods:
     - `create_run()` - Create new workflow run
     - `update_run_status()` - Update run status and output
     - `get_run()` - Retrieve run by ID

3. **NodeRunService** (`app/services/node_run_service.py`)
   - Manages NodeExecution records
   - Methods:
     - `create_node_run()` - Create node execution record
     - `update_node_run()` - Update node execution status
     - `get_node_run()` - Retrieve node execution by ID

4. **NodeHandlerService** (`app/services/node_handler_service.py`)
   - Dispatches node execution to appropriate handlers
   - Methods:
     - `execute_node()` - Execute a node via its handler
     - `get_handler()` - Get handler for node type
     - `register_handler()` - Register custom handlers
     - `list_node_types()` - List available node types

### Node Handlers (Placeholder Implementations)

All handlers return dummy data for now. Real implementations will be added in Step 7.

1. **LLMCallHandler** - Returns mock LLM responses
2. **HTTPRequestHandler** - Returns mock HTTP responses
3. **FAISSSearchHandler** - Returns mock search results
4. **DBWriteHandler** - Returns mock database operation results

## Execution Flow

```
1. User calls POST /api/workflows/{workflow_id}/execute
2. ExecutionService.execute_workflow() is called:
   a. Load workflow, nodes, and edges from database
   b. Validate graph structure (GraphService.validate_graph)
   c. Get execution order (topological sort)
   d. Create WorkflowRun record (status="running")
   e. Initialize context dict for storing outputs
   f. For each node in execution order:
      - Create NodeExecution record (status="running")
      - Execute node via NodeHandlerService
      - Store output in context
      - Update NodeExecution (status="completed")
   g. Update WorkflowRun (status="completed")
   h. Return execution results
3. If any error occurs:
   - Mark WorkflowRun as "failed"
   - Mark current NodeExecution as "failed"
   - Return error response
```

## Testing

### Prerequisites

1. Server running: `uvicorn app.main:app --reload`
2. Database setup with migrations applied
3. User registered and authenticated (JWT token)

### Step 1: Create a Simple Workflow

```bash
# Register and login to get token
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'

# Save the token
TOKEN="<your_access_token>"

# Create workflow
curl -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Execution Workflow",
    "description": "A workflow to test the execution engine"
  }'

# Save workflow_id
WORKFLOW_ID="<returned_workflow_id>"
```

### Step 2: Add Nodes

```bash
# Node 1: LLM Call
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "generate_text",
    "node_type": "llm_call",
    "config": {
      "prompt_template": "Generate a creative story about {topic}",
      "temperature": 0.8,
      "max_tokens": 200
    },
    "position_x": 100,
    "position_y": 100
  }'

# Save node1_id
NODE1_ID="<returned_node_id>"

# Node 2: HTTP Request
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "send_webhook",
    "node_type": "http_request",
    "config": {
      "url": "https://webhook.site/unique-id",
      "method": "POST",
      "headers": {"Content-Type": "application/json"}
    },
    "position_x": 300,
    "position_y": 100
  }'

# Save node2_id
NODE2_ID="<returned_node_id>"

# Node 3: FAISS Search
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "search_documents",
    "node_type": "faiss_search",
    "config": {
      "collection_name": "my_docs",
      "query": "artificial intelligence",
      "top_k": 5
    },
    "position_x": 500,
    "position_y": 100
  }'

# Save node3_id
NODE3_ID="<returned_node_id>"
```

### Step 3: Connect Nodes with Edges

```bash
# Edge: Node 1 -> Node 2
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/edges \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_node_id": "'$NODE1_ID'",
    "target_node_id": "'$NODE2_ID'"
  }'

# Edge: Node 2 -> Node 3
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/edges \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_node_id": "'$NODE2_ID'",
    "target_node_id": "'$NODE3_ID'"
  }'
```

### Step 4: Execute the Workflow

```bash
# Execute workflow
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "topic": "space exploration",
      "user_preferences": {"language": "en"}
    }
  }'
```

**Expected Response:**

```json
{
  "workflow_run_id": "uuid-here",
  "status": "completed",
  "output": {
    "results": [
      {
        "text": "[FAISS Result 1] Match for query: artificial intelligence...",
        "score": 0.95,
        "metadata": {"source": "doc_1"}
      },
      {
        "text": "[FAISS Result 2] Match for query: artificial intelligence...",
        "score": 0.85,
        "metadata": {"source": "doc_2"}
      },
      {
        "text": "[FAISS Result 3] Match for query: artificial intelligence...",
        "score": 0.75,
        "metadata": {"source": "doc_3"}
      }
    ],
    "query": "artificial intelligence",
    "collection_name": "my_docs",
    "total_results": 5,
    "status": "success"
  },
  "node_outputs": {
    "node1-uuid": {
      "response": "[LLM Response] Processed prompt: Generate a creative story about {topic}...",
      "model": "qwen-0.6b",
      "temperature": 0.8,
      "tokens_used": 150,
      "status": "success"
    },
    "node2-uuid": {
      "status_code": 200,
      "response": {
        "message": "[HTTP POST] Request to https://webhook.site/unique-id completed",
        "data": {"placeholder": "data"}
      },
      "headers": {"content-type": "application/json"},
      "status": "success"
    },
    "node3-uuid": {
      "results": [...],
      "query": "artificial intelligence",
      "collection_name": "my_docs",
      "total_results": 5,
      "status": "success"
    }
  }
}
```

### Step 5: Get Workflow Run Details

```bash
# Get run details
RUN_ID="<workflow_run_id_from_previous_response>"

curl -X GET http://localhost:8000/api/workflows/$WORKFLOW_ID/runs/$RUN_ID \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**

```json
{
  "id": "run-uuid",
  "workflow_id": "workflow-uuid",
  "status": "completed",
  "input_data": {
    "topic": "space exploration",
    "user_preferences": {"language": "en"}
  },
  "output_data": {
    "results": [...],
    "query": "artificial intelligence",
    "collection_name": "my_docs",
    "total_results": 5,
    "status": "success"
  },
  "error_message": null,
  "started_at": "2025-11-24T10:30:00Z",
  "completed_at": "2025-11-24T10:30:05Z"
}
```

## Testing Error Scenarios

### Test 1: Empty Workflow (No Nodes)

```bash
# Create empty workflow
curl -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Empty Workflow",
    "description": "No nodes"
  }'

EMPTY_WORKFLOW_ID="<returned_id>"

# Try to execute
curl -X POST http://localhost:8000/api/workflows/$EMPTY_WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected: 400 Bad Request** - "Workflow has no nodes to execute"

### Test 2: Workflow with Cycle

```bash
# Create workflow with 3 nodes in a cycle
# Node A -> Node B -> Node C -> Node A

# After creating nodes, add edges that form a cycle:
# Create edges: A->B, B->C, C->A

# Try to execute
curl -X POST http://localhost:8000/api/workflows/$CYCLE_WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected: 400 Bad Request** - "Invalid workflow graph: Cycle detected"

### Test 3: Workflow with No Start Node

```bash
# Create workflow where all nodes have incoming edges
# Node A -> Node B
# Node C -> Node A
# This creates a situation where no node is a start node

# Try to execute
curl -X POST http://localhost:8000/api/workflows/$NO_START_WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected: 400 Bad Request** - "Invalid workflow graph: No start nodes found"

## API Endpoints

### Execute Workflow

**POST** `/api/workflows/{workflow_id}/execute`

**Headers:**
- `Authorization: Bearer <token>`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "input_data": {
    "key": "value"
  }
}
```

**Response (201 Created):**
```json
{
  "workflow_run_id": "uuid",
  "status": "completed",
  "output": {...},
  "node_outputs": {...}
}
```

### Get Workflow Run

**GET** `/api/workflows/{workflow_id}/runs/{run_id}`

**Headers:**
- `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "id": "uuid",
  "workflow_id": "uuid",
  "status": "completed",
  "input_data": {...},
  "output_data": {...},
  "error_message": null,
  "started_at": "timestamp",
  "completed_at": "timestamp"
}
```

## Database Records

### WorkflowRun Table

After execution, check the `workflow_runs` table:

```sql
SELECT * FROM workflow_runs ORDER BY created_at DESC LIMIT 1;
```

Fields:
- `id` - UUID
- `workflow_id` - Reference to workflow
- `user_id` - User who executed
- `status` - "running", "completed", or "failed"
- `input_data` - JSONB with input
- `output_data` - JSONB with final output
- `error_message` - Error if failed
- `started_at` - Timestamp
- `completed_at` - Timestamp

### NodeExecution Table

Check node execution records:

```sql
SELECT * FROM node_executions WHERE workflow_run_id = '<run_id>' ORDER BY execution_order;
```

Fields:
- `id` - UUID
- `workflow_run_id` - Reference to workflow run
- `node_id` - Reference to node
- `status` - "running", "completed", or "failed"
- `execution_order` - Order in which node was executed
- `output_data` - JSONB with node output
- `error_message` - Error if failed
- `started_at` - Timestamp
- `completed_at` - Timestamp

## Next Steps

Once the execution engine is working:

1. **Step 7**: Implement real node handlers
   - Integrate Qwen model for LLMCallHandler
   - Use httpx for HTTPRequestHandler
   - Integrate FAISS for FAISSSearchHandler
   - Implement database operations for DBWriteHandler

2. **Add conditional branching**
   - Support for conditional edges
   - Multiple execution paths

3. **Add parallel execution**
   - Execute independent nodes in parallel
   - Use asyncio.gather for concurrent execution

4. **Add workflow variables**
   - Global variables accessible to all nodes
   - Variable interpolation in node configs

5. **Add error handling and retries**
   - Retry failed nodes
   - Configurable retry policies
   - Error recovery strategies

## Status

✅ **COMPLETE** - Execution engine fully implemented with:
- Complete workflow execution orchestration
- WorkflowRun and NodeExecution tracking
- Graph validation before execution
- Node handler dispatching
- Error handling and status updates
- Placeholder node handlers (returning dummy data)
- REST API endpoints for execution

🔄 **READY** - For real node handler implementation in Step 7





