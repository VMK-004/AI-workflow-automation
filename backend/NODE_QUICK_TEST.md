# Node CRUD - Quick Test Guide

## 🚀 5-Minute Test

### Step 1: Login & Create Workflow
```json
POST /api/auth/login
{
  "username": "alice",
  "password": "secret123"
}
→ Copy access_token

POST /api/workflows
{
  "name": "Test Workflow"
}
→ Copy workflow_id
```

### Step 2: Authorize in Swagger
- Click "Authorize" button
- Paste token
- Click "Authorize"

### Step 3: Create Nodes

#### LLM Node
```json
POST /api/workflows/{workflow_id}/nodes
{
  "name": "LLM Node",
  "node_type": "llm_call",
  "config": {
    "prompt_template": "Summarize: {input}",
    "temperature": 0.7,
    "max_tokens": 256
  },
  "position_x": 100,
  "position_y": 100
}
```

#### HTTP Node
```json
POST /api/workflows/{workflow_id}/nodes
{
  "name": "API Call",
  "node_type": "http_request",
  "config": {
    "method": "POST",
    "url": "https://api.example.com/data"
  },
  "position_x": 300,
  "position_y": 100
}
```

#### Vector Search Node
```json
POST /api/workflows/{workflow_id}/nodes
{
  "name": "Search",
  "node_type": "faiss_search",
  "config": {
    "collection_name": "documents",
    "query": "{input}",
    "top_k": 5
  },
  "position_x": 500,
  "position_y": 100
}
```

### Step 4: Test Other Operations

```bash
# List nodes
GET /api/workflows/{workflow_id}/nodes

# Get specific node
GET /api/workflows/{workflow_id}/nodes/{node_id}

# Update node
PUT /api/workflows/{workflow_id}/nodes/{node_id}
{
  "name": "Updated Name",
  "position_x": 150
}

# Delete node
DELETE /api/workflows/{workflow_id}/nodes/{node_id}
```

---

## ✅ Expected Results

| Test | Expected |
|------|----------|
| Create Node | 201 Created with node object |
| List Nodes | 200 OK with array |
| Get Node | 200 OK with node object |
| Update Node | 200 OK with updated node |
| Delete Node | 204 No Content |

---

## 🔐 Authorization Tests

### Test 1: Workflow Ownership
1. User A creates workflow
2. User B tries to add node to A's workflow
3. **Result:** 404 Workflow not found ✅

### Test 2: Node Access
1. User A creates workflow + node
2. User B tries to get A's node
3. **Result:** 404 Node not found ✅

---

## 🎯 Node Type Examples

### LLM Call
```json
{
  "node_type": "llm_call",
  "config": {
    "prompt_template": "Question: {input}",
    "temperature": 0.7,
    "max_tokens": 256
  }
}
```

### HTTP Request
```json
{
  "node_type": "http_request",
  "config": {
    "method": "GET",
    "url": "https://api.example.com/users/{input}",
    "headers": {
      "Authorization": "Bearer token"
    }
  }
}
```

### FAISS Search
```json
{
  "node_type": "faiss_search",
  "config": {
    "collection_name": "my_docs",
    "query": "{input}",
    "top_k": 10
  }
}
```

### DB Write
```json
{
  "node_type": "db_write",
  "config": {
    "table": "results",
    "data": {
      "content": "{input}",
      "processed_at": "now()"
    }
  }
}
```

---

## 🐍 Python One-Liner Test

```python
import requests; base = "http://localhost:8000"; token = requests.post(f"{base}/api/auth/login", json={"username":"test","password":"test123"}).json()["access_token"]; h = {"Authorization": f"Bearer {token}"}; wf = requests.post(f"{base}/api/workflows", headers=h, json={"name":"Test"}).json(); wf_id = wf["id"]; node = requests.post(f"{base}/api/workflows/{wf_id}/nodes", headers=h, json={"name":"Node1","node_type":"llm_call","config":{"prompt":"Hello"},"position_x":100,"position_y":100}).json(); print("Created:", node["name"]); print("List:", len(requests.get(f"{base}/api/workflows/{wf_id}/nodes", headers=h).json())); requests.put(f"{base}/api/workflows/{wf_id}/nodes/{node['id']}", headers=h, json={"name":"Updated"}); print("Updated:", requests.get(f"{base}/api/workflows/{wf_id}/nodes/{node['id']}", headers=h).json()["name"])
```

---

## 📊 Complete Workflow Example

```python
import requests

BASE = "http://localhost:8000"

# 1. Setup
token = requests.post(f"{BASE}/api/auth/login", 
    json={"username":"alice","password":"secret123"}).json()["access_token"]
h = {"Authorization": f"Bearer {token}"}

# 2. Create workflow
wf = requests.post(f"{BASE}/api/workflows", headers=h,
    json={"name":"My Pipeline"}).json()
wf_id = wf["id"]

# 3. Add nodes
node1 = requests.post(f"{BASE}/api/workflows/{wf_id}/nodes", headers=h,
    json={
        "name": "Extract",
        "node_type": "llm_call",
        "config": {"prompt_template": "Extract: {input}"},
        "position_x": 100,
        "position_y": 100
    }).json()

node2 = requests.post(f"{BASE}/api/workflows/{wf_id}/nodes", headers=h,
    json={
        "name": "Transform",
        "node_type": "http_request",
        "config": {"method": "POST", "url": "https://api.example.com"},
        "position_x": 300,
        "position_y": 100
    }).json()

node3 = requests.post(f"{BASE}/api/workflows/{wf_id}/nodes", headers=h,
    json={
        "name": "Load",
        "node_type": "db_write",
        "config": {"table": "results"},
        "position_x": 500,
        "position_y": 100
    }).json()

# 4. Verify
nodes = requests.get(f"{BASE}/api/workflows/{wf_id}/nodes", headers=h).json()
print(f"Created {len(nodes)} nodes:")
for node in nodes:
    print(f"  - {node['name']} ({node['node_type']}) at ({node['position_x']}, {node['position_y']})")
```

---

## ✨ All Endpoints

```
✅ GET    /api/workflows/{wf_id}/nodes              (List)
✅ POST   /api/workflows/{wf_id}/nodes              (Create)
✅ GET    /api/workflows/{wf_id}/nodes/{id}         (Get)
✅ PUT    /api/workflows/{wf_id}/nodes/{id}         (Update)
✅ DELETE /api/workflows/{wf_id}/nodes/{id}         (Delete)
```

**All require authentication + workflow ownership!**

---

## 🎯 Success Criteria

- [x] Can create nodes in workflow
- [x] Can list all nodes
- [x] Can get specific node
- [x] Can update node config
- [x] Can update node position
- [x] Can delete node
- [x] Workflow ownership verified
- [x] Proper error messages
- [x] Correct status codes

---

**Test now: http://localhost:8000/docs** 🚀





