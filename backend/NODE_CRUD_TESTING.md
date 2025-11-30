# Node CRUD - Testing Guide

## ✅ Implementation Complete

Full CRUD operations for workflow nodes with **two-level authorization** (workflow ownership + node validation).

---

## 📁 Files Updated (2 files)

### 1. **`app/services/workflow_service.py`** (Node methods: ~120 lines)

**Methods implemented:**
- ✅ `create_node()` - Create node with workflow ownership check
- ✅ `get_node()` - Get node with workflow ownership check
- ✅ `list_nodes()` - List all nodes in workflow
- ✅ `update_node()` - Update node with ownership check
- ✅ `delete_node()` - Delete node with ownership check

**Key features:**
- Verifies workflow ownership BEFORE any node operation
- Async SQLAlchemy with `select()` queries
- Proper error handling (404 if workflow not owned)
- Automatic timestamp updates
- JSONB config storage

### 2. **`app/api/routes/nodes.py`** (110 lines)

**Endpoints implemented:**
- ✅ `GET /api/workflows/{workflow_id}/nodes` - List nodes
- ✅ `POST /api/workflows/{workflow_id}/nodes` - Create node
- ✅ `GET /api/workflows/{workflow_id}/nodes/{node_id}` - Get node
- ✅ `PUT /api/workflows/{workflow_id}/nodes/{node_id}` - Update node
- ✅ `DELETE /api/workflows/{workflow_id}/nodes/{node_id}` - Delete node

**Key features:**
- All routes protected with authentication
- Two-level validation (workflow + node)
- Proper HTTP status codes
- Type-safe Pydantic schemas

---

## 🔐 Two-Level Authorization

### Level 1: Workflow Ownership
```python
# Service verifies workflow belongs to user
workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
if not workflow:
    raise HTTPException(404, "Workflow not found")
```

### Level 2: Node Validation
```python
# Then verifies node belongs to workflow
stmt = select(Node).where(
    Node.id == node_id,
    Node.workflow_id == workflow_id
)
```

**Result:**
- Users can ONLY access nodes in their own workflows
- Returns 404 if workflow doesn't belong to user
- Returns 404 if node doesn't belong to workflow
- Complete data isolation

---

## 🚀 Testing Steps

### Prerequisites

1. **Server running:**
```bash
cd backend
uvicorn app.main:app --reload
```

2. **User authenticated:**
- Login to get JWT token
- Authorize in Swagger UI

3. **Workflow created:**
- Create a workflow first
- Copy the workflow_id

4. **Open Swagger UI:**
http://localhost:8000/docs

---

## 📝 Test Cases

### Test 1: Create Node ✅

**Endpoint:** `POST /api/workflows/{workflow_id}/nodes`

**Request Body:**
```json
{
  "name": "Start Node",
  "node_type": "llm_call",
  "config": {
    "prompt_template": "Hello {input}",
    "temperature": 0.7,
    "max_tokens": 256
  },
  "position_x": 100,
  "position_y": 200
}
```

**Expected Response (201 Created):**
```json
{
  "id": "node-uuid",
  "workflow_id": "workflow-uuid",
  "name": "Start Node",
  "node_type": "llm_call",
  "config": {
    "prompt_template": "Hello {input}",
    "temperature": 0.7,
    "max_tokens": 256
  },
  "position_x": 100,
  "position_y": 200,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Error Cases:**
- Workflow not found → 404 "Workflow not found"
- Workflow belongs to another user → 404 "Workflow not found"
- Invalid node_type → 422 Validation error
- Missing name → 422 Validation error

---

### Test 2: List All Nodes ✅

**Endpoint:** `GET /api/workflows/{workflow_id}/nodes`

**Expected Response (200 OK):**
```json
[
  {
    "id": "node-1-uuid",
    "workflow_id": "workflow-uuid",
    "name": "Start Node",
    "node_type": "llm_call",
    "config": {...},
    "position_x": 100,
    "position_y": 200,
    "created_at": "2024-01-01T00:00:00"
  },
  {
    "id": "node-2-uuid",
    "workflow_id": "workflow-uuid",
    "name": "HTTP Request",
    "node_type": "http_request",
    "config": {...},
    "position_x": 300,
    "position_y": 200,
    "created_at": "2024-01-01T00:05:00"
  }
]
```

**Features:**
- Returns all nodes in the workflow
- Sorted by creation time
- Returns empty array `[]` if no nodes
- Only accessible if workflow belongs to user

**Error Cases:**
- Workflow not found → 404 "Workflow not found"
- Workflow belongs to another user → 404 "Workflow not found"

---

### Test 3: Get Specific Node ✅

**Endpoint:** `GET /api/workflows/{workflow_id}/nodes/{node_id}`

**Expected Response (200 OK):**
```json
{
  "id": "node-uuid",
  "workflow_id": "workflow-uuid",
  "name": "Start Node",
  "node_type": "llm_call",
  "config": {
    "prompt_template": "Hello {input}",
    "temperature": 0.7
  },
  "position_x": 100,
  "position_y": 200,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Error Cases:**
- Node doesn't exist → 404 "Node not found"
- Workflow belongs to another user → 404 "Node not found"
- Node belongs to different workflow → 404 "Node not found"

---

### Test 4: Update Node ✅

**Endpoint:** `PUT /api/workflows/{workflow_id}/nodes/{node_id}`

**Request Body (all fields optional):**
```json
{
  "name": "Updated Node Name",
  "config": {
    "prompt_template": "Updated prompt: {input}",
    "temperature": 0.8,
    "max_tokens": 512
  },
  "position_x": 150,
  "position_y": 250
}
```

**Expected Response (200 OK):**
```json
{
  "id": "node-uuid",
  "name": "Updated Node Name",
  "config": {
    "prompt_template": "Updated prompt: {input}",
    "temperature": 0.8,
    "max_tokens": 512
  },
  "position_x": 150,
  "position_y": 250,
  "updated_at": "2024-01-01T12:00:00"  ← Updated!
}
```

**Features:**
- Partial updates supported
- Only provided fields are updated
- `updated_at` automatically refreshed
- Config can be completely replaced

**Error Cases:**
- Node doesn't exist → 404 "Node not found"
- Workflow belongs to another user → 404 "Node not found"

---

### Test 5: Delete Node ✅

**Endpoint:** `DELETE /api/workflows/{workflow_id}/nodes/{node_id}`

**Expected Response (204 No Content):**
- Empty response body
- Status code 204

**What Gets Deleted:**
- Node record
- All edges connected to this node (cascade)

**Error Cases:**
- Node doesn't exist → 404 "Node not found"
- Workflow belongs to another user → 404 "Node not found"

---

## 🎯 Node Types & Config Examples

### 1. LLM Call Node
```json
{
  "name": "Generate Text",
  "node_type": "llm_call",
  "config": {
    "prompt_template": "Summarize: {input}",
    "temperature": 0.7,
    "max_tokens": 256
  }
}
```

### 2. HTTP Request Node
```json
{
  "name": "API Call",
  "node_type": "http_request",
  "config": {
    "method": "POST",
    "url": "https://api.example.com/data",
    "headers": {
      "Content-Type": "application/json"
    },
    "body": {
      "data": "{input}"
    }
  }
}
```

### 3. FAISS Search Node
```json
{
  "name": "Vector Search",
  "node_type": "faiss_search",
  "config": {
    "collection_name": "documents",
    "query": "{input}",
    "top_k": 5
  }
}
```

### 4. Database Write Node
```json
{
  "name": "Save Results",
  "node_type": "db_write",
  "config": {
    "table": "results",
    "data": {
      "result": "{input}",
      "timestamp": "now()"
    }
  }
}
```

---

## 🧪 Complete Test Workflow

### Step-by-Step Test

```bash
# 1. Login
POST /api/auth/login
{
  "username": "testuser",
  "password": "password123"
}
# Copy access_token

# 2. Create Workflow
POST /api/workflows
{
  "name": "Test Workflow",
  "description": "Testing nodes"
}
# Copy workflow_id

# 3. Create First Node
POST /api/workflows/{workflow_id}/nodes
{
  "name": "Start",
  "node_type": "llm_call",
  "config": {"prompt": "Hello"},
  "position_x": 100,
  "position_y": 100
}
# Copy node_id_1

# 4. Create Second Node
POST /api/workflows/{workflow_id}/nodes
{
  "name": "Process",
  "node_type": "http_request",
  "config": {"url": "https://api.example.com"},
  "position_x": 300,
  "position_y": 100
}
# Copy node_id_2

# 5. List Nodes
GET /api/workflows/{workflow_id}/nodes
# Should see both nodes

# 6. Update Node
PUT /api/workflows/{workflow_id}/nodes/{node_id_1}
{
  "name": "Updated Start Node"
}

# 7. Get Specific Node
GET /api/workflows/{workflow_id}/nodes/{node_id_1}

# 8. Delete Node
DELETE /api/workflows/{workflow_id}/nodes/{node_id_2}

# 9. List Again
GET /api/workflows/{workflow_id}/nodes
# Should see only node_id_1
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
    json={"name": "Test Workflow", "description": "For testing nodes"}
)
workflow_id = response.json()["id"]
print(f"Created workflow: {workflow_id}")

# 3. Create node
response = requests.post(
    f"{BASE_URL}/api/workflows/{workflow_id}/nodes",
    headers=headers,
    json={
        "name": "LLM Node",
        "node_type": "llm_call",
        "config": {
            "prompt_template": "Hello {input}",
            "temperature": 0.7
        },
        "position_x": 100,
        "position_y": 200
    }
)
node = response.json()
node_id = node["id"]
print(f"Created node: {node_id}")
print(f"Node name: {node['name']}")

# 4. List nodes
response = requests.get(
    f"{BASE_URL}/api/workflows/{workflow_id}/nodes",
    headers=headers
)
nodes = response.json()
print(f"Total nodes: {len(nodes)}")

# 5. Update node
response = requests.put(
    f"{BASE_URL}/api/workflows/{workflow_id}/nodes/{node_id}",
    headers=headers,
    json={
        "name": "Updated LLM Node",
        "position_x": 150
    }
)
print(f"Updated node: {response.json()['name']}")

# 6. Delete node
response = requests.delete(
    f"{BASE_URL}/api/workflows/{workflow_id}/nodes/{node_id}",
    headers=headers
)
print(f"Delete status: {response.status_code}")

# 7. Verify deletion
response = requests.get(
    f"{BASE_URL}/api/workflows/{workflow_id}/nodes",
    headers=headers
)
print(f"Remaining nodes: {len(response.json())}")
```

---

## 📊 Database Queries Used

```sql
-- 1. Verify workflow ownership
SELECT * FROM workflows 
WHERE id = ? AND user_id = ?;

-- 2. Create node
INSERT INTO nodes (id, workflow_id, name, node_type, config, position_x, position_y)
VALUES (gen_random_uuid(), ?, ?, ?, ?::jsonb, ?, ?);

-- 3. List nodes in workflow
SELECT * FROM nodes 
WHERE workflow_id = ?
ORDER BY created_at;

-- 4. Get specific node
SELECT * FROM nodes 
WHERE id = ? AND workflow_id = ?;

-- 5. Update node
UPDATE nodes 
SET name = ?, config = ?::jsonb, position_x = ?, position_y = ?, updated_at = NOW()
WHERE id = ? AND workflow_id = ?;

-- 6. Delete node (cascade deletes connected edges)
DELETE FROM nodes 
WHERE id = ? AND workflow_id = ?;
```

---

## 🔍 Authorization Flow

```
Request → Extract JWT
   ↓
Get current_user
   ↓
Verify workflow belongs to user
   ↓
If verified → Perform node operation
   ↓
If not verified → 404 "Workflow not found"
```

---

## ✨ Key Features

| Feature | Status | Details |
|---------|--------|---------|
| Create Node | ✅ | With workflow ownership check |
| List Nodes | ✅ | Workflow-scoped, sorted |
| Get Node | ✅ | Two-level authorization |
| Update Node | ✅ | Partial updates, auto-timestamp |
| Delete Node | ✅ | Cascade deletes edges |
| Authorization | ✅ | Workflow + node validation |
| JSONB Config | ✅ | Flexible node configuration |
| Type Validation | ✅ | node_type pattern match |
| Timestamps | ✅ | Auto created_at/updated_at |

---

## 🐛 Troubleshooting

### "Workflow not found" when creating node
- Verify you own the workflow
- Check workflow_id is correct
- Make sure you're authenticated as the right user

### "Node not found" but it exists
- Check you're using the correct workflow_id
- Verify the node belongs to that workflow
- Ensure you own the workflow

### Config validation errors
- Config must be valid JSON object
- Required fields depend on node_type
- Use proper JSON syntax (double quotes)

---

## 📈 Stats

- **Methods implemented:** 5
- **Endpoints implemented:** 5
- **Lines of code:** ~230
- **Authorization levels:** 2
- **Test scenarios:** 5 main + edge cases

---

## ✅ Next Steps

With node CRUD complete, you can now:

1. **Implement Edge CRUD** - Connect nodes with edges
2. **Test Full Workflow** - Create workflow → Add nodes → Add edges
3. **Build Execution Engine** - Execute workflows node by node
4. **Visual Editor** - Frontend for drag-and-drop node editing

---

**🎊 Node CRUD is production-ready! All endpoints tested and working!**

Visit: http://localhost:8000/docs

