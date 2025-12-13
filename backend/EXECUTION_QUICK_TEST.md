# Quick Execution Engine Test

## Quick Start (Copy-Paste Commands)

```bash
# 1. Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"exectest","email":"exec@test.com","password":"test123"}'

# 2. Login and save token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"exectest","password":"test123"}'

# Copy the access_token from response
TOKEN="<paste_token_here>"

# 3. Create workflow
curl -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Execution Test","description":"Test workflow execution"}'

# Copy the id from response
WORKFLOW_ID="<paste_workflow_id_here>"

# 4. Create Node 1 (LLM)
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"llm_node",
    "node_type":"llm_call",
    "config":{"prompt_template":"Generate text about {topic}","temperature":0.8},
    "position_x":100,
    "position_y":100
  }'

# Copy the id
NODE1_ID="<paste_node1_id_here>"

# 5. Create Node 2 (HTTP)
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"http_node",
    "node_type":"http_request",
    "config":{"url":"https://api.example.com","method":"POST"},
    "position_x":300,
    "position_y":100
  }'

# Copy the id
NODE2_ID="<paste_node2_id_here>"

# 6. Create Node 3 (FAISS)
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"search_node",
    "node_type":"faiss_search",
    "config":{"collection_name":"docs","query":"AI","top_k":3},
    "position_x":500,
    "position_y":100
  }'

# Copy the id
NODE3_ID="<paste_node3_id_here>"

# 7. Connect nodes: Node1 -> Node2
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/edges \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"source_node_id\":\"$NODE1_ID\",\"target_node_id\":\"$NODE2_ID\"}"

# 8. Connect nodes: Node2 -> Node3
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/edges \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"source_node_id\":\"$NODE2_ID\",\"target_node_id\":\"$NODE3_ID\"}"

# 9. EXECUTE THE WORKFLOW! 🚀
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"input_data":{"topic":"AI and machine learning"}}'

# You should see a response with:
# - workflow_run_id
# - status: "completed"
# - output: {...}
# - node_outputs: {node1: {...}, node2: {...}, node3: {...}}

# 10. Get run details
# Copy workflow_run_id from previous response
RUN_ID="<paste_run_id_here>"

curl -X GET http://localhost:8000/api/workflows/$WORKFLOW_ID/runs/$RUN_ID \
  -H "Authorization: Bearer $TOKEN"
```

## Expected Output

When you execute the workflow, you should see:

```json
{
  "workflow_run_id": "abc-123-def-456",
  "status": "completed",
  "output": {
    "results": [
      {
        "text": "[FAISS Result 1] Match for query: AI...",
        "score": 0.95,
        "metadata": {"source": "doc_1"}
      },
      {
        "text": "[FAISS Result 2] Match for query: AI...",
        "score": 0.85,
        "metadata": {"source": "doc_2"}
      },
      {
        "text": "[FAISS Result 3] Match for query: AI...",
        "score": 0.75,
        "metadata": {"source": "doc_3"}
      }
    ],
    "query": "AI",
    "collection_name": "docs",
    "total_results": 3,
    "status": "success"
  },
  "node_outputs": {
    "node1-uuid": {
      "response": "[LLM Response] Processed prompt: Generate text about {topic}...",
      "model": "qwen-0.6b",
      "temperature": 0.8,
      "tokens_used": 150,
      "status": "success"
    },
    "node2-uuid": {
      "status_code": 200,
      "response": {
        "message": "[HTTP POST] Request to https://api.example.com completed",
        "data": {"placeholder": "data"}
      },
      "headers": {"content-type": "application/json"},
      "status": "success"
    },
    "node3-uuid": {
      "results": [...],
      "query": "AI",
      "collection_name": "docs",
      "total_results": 3,
      "status": "success"
    }
  }
}
```

## What Just Happened?

1. ✅ Graph validated (no cycles, has start node, all nodes reachable)
2. ✅ Execution order determined: [Node1 → Node2 → Node3]
3. ✅ WorkflowRun created with status="running"
4. ✅ Node1 executed → output stored
5. ✅ Node2 executed → output stored
6. ✅ Node3 executed → output stored
7. ✅ WorkflowRun updated to status="completed"
8. ✅ All outputs returned to user

## Check Database

```sql
-- See workflow runs
SELECT id, workflow_id, status, started_at, completed_at 
FROM workflow_runs 
ORDER BY created_at DESC 
LIMIT 5;

-- See node executions
SELECT ne.id, n.name, ne.status, ne.execution_order, ne.started_at, ne.completed_at
FROM node_executions ne
JOIN nodes n ON ne.node_id = n.id
WHERE ne.workflow_run_id = '<your_run_id>'
ORDER BY ne.execution_order;
```

## Next Steps

✅ Execution engine is working!

Now you can:
1. Test with different node types
2. Test error scenarios (cycles, no start nodes)
3. Implement real node handlers in Step 7
4. Build the frontend to visualize execution

---

**Status**: 🟢 Ready to test!





