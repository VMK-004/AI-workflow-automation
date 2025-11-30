# Edge CRUD - Testing Guide

## ✅ Implementation Complete

Full CRUD operations for workflow edges with **three-level validation** (workflow ownership + node validation + edge operations).

---

## 📁 Files Updated (2 files)

### 1. **`app/services/workflow_service.py`** (Edge methods: ~100 lines)

**Methods implemented:**
- ✅ `create_edge()` - Create edge with node validation
- ✅ `get_edge()` - Get edge with workflow ownership check
- ✅ `list_edges()` - List all edges in workflow
- ✅ `delete_edge()` - Delete edge with ownership check

**Key features:**
- Verifies workflow ownership BEFORE any edge operation
- Validates BOTH nodes belong to the workflow
- Async SQLAlchemy with `select()` queries
- Proper error handling (404 for workflow, 400 for invalid nodes)
- Transaction safety

### 2. **`app/api/routes/edges.py`** (95 lines)

**Endpoints implemented:**
- ✅ `GET /api/workflows/{workflow_id}/edges` - List edges
- ✅ `POST /api/workflows/{workflow_id}/edges` - Create edge
- ✅ `GET /api/workflows/{workflow_id}/edges/{edge_id}` - Get edge
- ✅ `DELETE /api/workflows/{workflow_id}/edges/{edge_id}` - Delete edge

**Key features:**
- All routes protected with authentication
- Three-level validation (workflow + nodes + edge)
- Proper HTTP status codes (200, 201, 204, 400, 404)
- Type-safe Pydantic schemas

---

## 🔐 Three-Level Validation

### Level 1: Workflow Ownership
```python
workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
if not workflow:
    raise HTTPException(404, "Workflow not found")
```

### Level 2: Source Node Validation
```python
source_node = await WorkflowService.get_node(db, workflow_id, source_node_id, user_id)
if not source_node:
    raise HTTPException(400, "Source node does not belong to this workflow")
```

### Level 3: Target Node Validation
```python
target_node = await WorkflowService.get_node(db, workflow_id, target_node_id, user_id)
if not target_node:
    raise HTTPException(400, "Target node does not belong to this workflow")
```

**Result:**
- Users can ONLY create edges in their own workflows
- Both nodes MUST exist in the same workflow
- Complete data isolation and graph integrity

---

## 🚀 Testing Steps

### Prerequisites

1. **Server running:**
```bash
cd backend
uvicorn app.main:app --reload
```

2. **User authenticated + Workflow + Nodes created:**
```bash
# Login
POST /api/auth/login

# Create workflow
POST /api/workflows

# Create at least 2 nodes
POST /api/workflows/{workflow_id}/nodes
```

3. **Open Swagger UI:**
http://localhost:8000/docs

---

## 📝 Test Cases

### Test 1: Create Edge ✅

**Endpoint:** `POST /api/workflows/{workflow_id}/edges`

**Request Body:**
```json
{
  "source_node_id": "node-1-uuid",
  "target_node_id": "node-2-uuid"
}
```

**Expected Response (201 Created):**
```json
{
  "id": "edge-uuid",
  "workflow_id": "workflow-uuid",
  "source_node_id": "node-1-uuid",
  "target_node_id": "node-2-uuid",
  "created_at": "2024-01-01T00:00:00"
}
```

**Error Cases:**
- Workflow not found → 404 "Workflow not found"
- Source node not in workflow → 400 "Source node does not belong to this workflow"
- Target node not in workflow → 400 "Target node does not belong to this workflow"
- Source node from different workflow → 400
- Target node from different workflow → 400

---

### Test 2: List All Edges ✅

**Endpoint:** `GET /api/workflows/{workflow_id}/edges`

**Expected Response (200 OK):**
```json
[
  {
    "id": "edge-1-uuid",
    "workflow_id": "workflow-uuid",
    "source_node_id": "node-1-uuid",
    "target_node_id": "node-2-uuid",
    "created_at": "2024-01-01T00:00:00"
  },
  {
    "id": "edge-2-uuid",
    "workflow_id": "workflow-uuid",
    "source_node_id": "node-2-uuid",
    "target_node_id": "node-3-uuid",
    "created_at": "2024-01-01T00:05:00"
  }
]
```

**Features:**
- Returns all edges in the workflow
- Sorted by creation time
- Returns empty array `[]` if no edges
- Only accessible if workflow belongs to user

**Error Cases:**
- Workflow not found → 404 "Workflow not found"
- Workflow belongs to another user → 404 "Workflow not found"

---

### Test 3: Get Specific Edge ✅

**Endpoint:** `GET /api/workflows/{workflow_id}/edges/{edge_id}`

**Expected Response (200 OK):**
```json
{
  "id": "edge-uuid",
  "workflow_id": "workflow-uuid",
  "source_node_id": "node-1-uuid",
  "target_node_id": "node-2-uuid",
  "created_at": "2024-01-01T00:00:00"
}
```

**Error Cases:**
- Edge doesn't exist → 404 "Edge not found"
- Workflow belongs to another user → 404 "Edge not found"
- Edge belongs to different workflow → 404 "Edge not found"

---

### Test 4: Delete Edge ✅

**Endpoint:** `DELETE /api/workflows/{workflow_id}/edges/{edge_id}`

**Expected Response (204 No Content):**
- Empty response body
- Status code 204

**What Gets Deleted:**
- Edge record connecting two nodes

**What Stays:**
- Both nodes remain intact
- Other edges remain intact

**Error Cases:**
- Edge doesn't exist → 404 "Edge not found"
- Workflow belongs to another user → 404 "Edge not found"

---

## 🎯 Complete Workflow Graph Test

### Build a Complete Pipeline

```bash
# 1. Login
POST /api/auth/login
{
  "username": "alice",
  "password": "secret123"
}
→ Get token

# 2. Create Workflow
POST /api/workflows
{
  "name": "Data Pipeline",
  "description": "Extract → Transform → Load"
}
→ Get workflow_id

# 3. Create Node 1 (Extract)
POST /api/workflows/{workflow_id}/nodes
{
  "name": "Extract",
  "node_type": "http_request",
  "config": {
    "method": "GET",
    "url": "https://api.example.com/data"
  },
  "position_x": 100,
  "position_y": 200
}
→ Get node_1_id

# 4. Create Node 2 (Transform)
POST /api/workflows/{workflow_id}/nodes
{
  "name": "Transform",
  "node_type": "llm_call",
  "config": {
    "prompt_template": "Transform: {input}"
  },
  "position_x": 300,
  "position_y": 200
}
→ Get node_2_id

# 5. Create Node 3 (Load)
POST /api/workflows/{workflow_id}/nodes
{
  "name": "Load",
  "node_type": "db_write",
  "config": {
    "table": "results"
  },
  "position_x": 500,
  "position_y": 200
}
→ Get node_3_id

# 6. Create Edge 1 (Extract → Transform)
POST /api/workflows/{workflow_id}/edges
{
  "source_node_id": "{node_1_id}",
  "target_node_id": "{node_2_id}"
}

# 7. Create Edge 2 (Transform → Load)
POST /api/workflows/{workflow_id}/edges
{
  "source_node_id": "{node_2_id}",
  "target_node_id": "{node_3_id}"
}

# 8. List All Edges
GET /api/workflows/{workflow_id}/edges
→ See 2 edges

# 9. Visualize the Graph
Extract (node_1) → Transform (node_2) → Load (node_3)

# 10. Delete an Edge
DELETE /api/workflows/{workflow_id}/edges/{edge_id}

# 11. List Again
GET /api/workflows/{workflow_id}/edges
→ See remaining edge
```

---

## 🐍 Python Test Script

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Login
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": "testuser", "password": "password123"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Create workflow
response = requests.post(
    f"{BASE_URL}/api/workflows",
    headers=headers,
    json={"name": "Test Pipeline", "description": "Testing edges"}
)
workflow_id = response.json()["id"]
print(f"Created workflow: {workflow_id}")

# 3. Create 3 nodes
nodes = []
for i, name in enumerate(["Extract", "Transform", "Load"], 1):
    response = requests.post(
        f"{BASE_URL}/api/workflows/{workflow_id}/nodes",
        headers=headers,
        json={
            "name": name,
            "node_type": "llm_call",
            "config": {"prompt": f"{name} step"},
            "position_x": i * 200,
            "position_y": 200
        }
    )
    node = response.json()
    nodes.append(node)
    print(f"Created node {i}: {node['name']} ({node['id']})")

# 4. Create edges to connect them
# Extract → Transform
response = requests.post(
    f"{BASE_URL}/api/workflows/{workflow_id}/edges",
    headers=headers,
    json={
        "source_node_id": nodes[0]["id"],
        "target_node_id": nodes[1]["id"]
    }
)
edge1 = response.json()
print(f"Created edge 1: {nodes[0]['name']} → {nodes[1]['name']}")

# Transform → Load
response = requests.post(
    f"{BASE_URL}/api/workflows/{workflow_id}/edges",
    headers=headers,
    json={
        "source_node_id": nodes[1]["id"],
        "target_node_id": nodes[2]["id"]
    }
)
edge2 = response.json()
print(f"Created edge 2: {nodes[1]['name']} → {nodes[2]['name']}")

# 5. List all edges
response = requests.get(
    f"{BASE_URL}/api/workflows/{workflow_id}/edges",
    headers=headers
)
edges = response.json()
print(f"\nTotal edges: {len(edges)}")
for edge in edges:
    print(f"  - Edge {edge['id']}: {edge['source_node_id']} → {edge['target_node_id']}")

# 6. Get specific edge
response = requests.get(
    f"{BASE_URL}/api/workflows/{workflow_id}/edges/{edge1['id']}",
    headers=headers
)
print(f"\nFetched edge: {response.json()['id']}")

# 7. Delete edge
response = requests.delete(
    f"{BASE_URL}/api/workflows/{workflow_id}/edges/{edge2['id']}",
    headers=headers
)
print(f"Delete status: {response.status_code}")

# 8. Verify deletion
response = requests.get(
    f"{BASE_URL}/api/workflows/{workflow_id}/edges",
    headers=headers
)
print(f"Remaining edges: {len(response.json())}")
```

---

## 📊 Graph Visualization Examples

### Linear Pipeline
```
[Extract] → [Transform] → [Load]
```

**Edges:**
- Extract → Transform
- Transform → Load

### Branching Pipeline
```
[Input] → [ProcessA]
       ↓
       → [ProcessB]
```

**Edges:**
- Input → ProcessA
- Input → ProcessB

### Converging Pipeline
```
[SourceA] ↘
           → [Merge] → [Output]
[SourceB] ↗
```

**Edges:**
- SourceA → Merge
- SourceB → Merge
- Merge → Output

### Complex Graph
```
[A] → [B] → [D]
  ↘   ↗   ↘
   [C]     [E]
```

**Edges:**
- A → B
- A → C
- B → D
- C → B
- D → E

---

## 📊 Database Queries Used

```sql
-- 1. Verify workflow ownership
SELECT * FROM workflows 
WHERE id = ? AND user_id = ?;

-- 2. Verify source node belongs to workflow
SELECT * FROM nodes 
WHERE id = ? AND workflow_id = ?;

-- 3. Verify target node belongs to workflow
SELECT * FROM nodes 
WHERE id = ? AND workflow_id = ?;

-- 4. Create edge
INSERT INTO edges (id, workflow_id, source_node_id, target_node_id)
VALUES (gen_random_uuid(), ?, ?, ?);

-- 5. List edges in workflow
SELECT * FROM edges 
WHERE workflow_id = ?
ORDER BY created_at;

-- 6. Get specific edge
SELECT * FROM edges 
WHERE id = ? AND workflow_id = ?;

-- 7. Delete edge
DELETE FROM edges 
WHERE id = ? AND workflow_id = ?;
```

---

## 🔍 Validation Flow

```
Request → Extract JWT
   ↓
Get current_user
   ↓
Verify workflow belongs to user
   ↓
If CREATE: Verify both nodes belong to workflow
   ↓
Perform edge operation
   ↓
Return result or 404/400
```

---

## ✨ Key Features

| Feature | Status | Details |
|---------|--------|---------|
| Create Edge | ✅ | With node validation |
| List Edges | ✅ | Workflow-scoped, sorted |
| Get Edge | ✅ | Three-level authorization |
| Delete Edge | ✅ | Ownership verified |
| Node Validation | ✅ | Both nodes checked |
| Workflow Auth | ✅ | User isolation |
| Graph Integrity | ✅ | Nodes must exist |
| Type Safety | ✅ | Pydantic validation |

---

## 🐛 Troubleshooting

### "Source node does not belong to this workflow"
- Verify source_node_id is correct
- Check node was created in THIS workflow
- Nodes from other workflows can't be connected

### "Target node does not belong to this workflow"
- Verify target_node_id is correct
- Check node was created in THIS workflow
- Can't connect to nodes in other workflows

### "Workflow not found"
- Verify you own the workflow
- Check workflow_id is correct
- Must be authenticated as correct user

### "Edge not found"
- Check edge_id is correct
- Verify edge belongs to this workflow
- Ensure you own the workflow

---

## 📈 Stats

- **Methods implemented:** 4
- **Endpoints implemented:** 4
- **Lines of code:** ~195
- **Validation levels:** 3
- **Test scenarios:** 4 main + edge cases

---

## ✅ Next Steps

With complete CRUD for workflows, nodes, and edges:

1. **Test Complete Graph** - Create full workflow with multiple nodes and edges
2. **Graph Validation** - Add cycle detection (DAG enforcement)
3. **Execution Engine** - Build workflow executor using the graph
4. **Topological Sort** - Determine node execution order
5. **Visual Editor** - Frontend for drag-and-drop workflow building

---

**🎊 Edge CRUD is production-ready! Full graph building capability!**

Visit: http://localhost:8000/docs

You can now create complete workflow graphs!

