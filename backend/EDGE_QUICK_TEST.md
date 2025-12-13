# Edge CRUD - Quick Test Guide

## 🚀 5-Minute Complete Workflow Test

### Step 1: Setup (Login + Workflow + Nodes)

```json
# 1. Login
POST /api/auth/login
{
  "username": "alice",
  "password": "secret123"
}
→ Copy access_token & authorize

# 2. Create Workflow
POST /api/workflows
{
  "name": "My Pipeline"
}
→ Copy workflow_id

# 3. Create Node 1
POST /api/workflows/{workflow_id}/nodes
{
  "name": "Start",
  "node_type": "llm_call",
  "config": {"prompt": "Begin"},
  "position_x": 100,
  "position_y": 200
}
→ Copy node_1_id

# 4. Create Node 2
POST /api/workflows/{workflow_id}/nodes
{
  "name": "Process",
  "node_type": "http_request",
  "config": {"url": "https://api.example.com"},
  "position_x": 300,
  "position_y": 200
}
→ Copy node_2_id

# 5. Create Node 3
POST /api/workflows/{workflow_id}/nodes
{
  "name": "End",
  "node_type": "db_write",
  "config": {"table": "results"},
  "position_x": 500,
  "position_y": 200
}
→ Copy node_3_id
```

### Step 2: Connect Nodes with Edges

```json
# 6. Create Edge 1 (Start → Process)
POST /api/workflows/{workflow_id}/edges
{
  "source_node_id": "{node_1_id}",
  "target_node_id": "{node_2_id}"
}

# 7. Create Edge 2 (Process → End)
POST /api/workflows/{workflow_id}/edges
{
  "source_node_id": "{node_2_id}",
  "target_node_id": "{node_3_id}"
}
```

### Step 3: Verify & Test

```bash
# 8. List all edges
GET /api/workflows/{workflow_id}/edges
→ See 2 edges

# 9. Get specific edge
GET /api/workflows/{workflow_id}/edges/{edge_id}

# 10. Delete an edge
DELETE /api/workflows/{workflow_id}/edges/{edge_id}

# 11. List again
GET /api/workflows/{workflow_id}/edges
→ See 1 edge remaining
```

---

## ✅ Expected Results

| Test | Expected |
|------|----------|
| Create Edge | 201 Created with edge object |
| List Edges | 200 OK with array |
| Get Edge | 200 OK with edge object |
| Delete Edge | 204 No Content |

---

## 🎯 Graph Patterns

### Linear Pipeline
```
[A] → [B] → [C]
```

**Edges:**
```json
{ "source_node_id": "A", "target_node_id": "B" }
{ "source_node_id": "B", "target_node_id": "C" }
```

### Branching
```
      → [B]
[A]
      → [C]
```

**Edges:**
```json
{ "source_node_id": "A", "target_node_id": "B" }
{ "source_node_id": "A", "target_node_id": "C" }
```

### Merging
```
[A] ↘
     → [C]
[B] ↗
```

**Edges:**
```json
{ "source_node_id": "A", "target_node_id": "C" }
{ "source_node_id": "B", "target_node_id": "C" }
```

### Complex
```
[A] → [B] → [D]
  ↘   ↗
   [C]
```

**Edges:**
```json
{ "source_node_id": "A", "target_node_id": "B" }
{ "source_node_id": "A", "target_node_id": "C" }
{ "source_node_id": "C", "target_node_id": "B" }
{ "source_node_id": "B", "target_node_id": "D" }
```

---

## 🐍 Python One-Liner Complete Test

```python
import requests; base = "http://localhost:8000"; token = requests.post(f"{base}/api/auth/login", json={"username":"test","password":"test123"}).json()["access_token"]; h = {"Authorization": f"Bearer {token}"}; wf = requests.post(f"{base}/api/workflows", headers=h, json={"name":"Test"}).json(); wf_id = wf["id"]; n1 = requests.post(f"{base}/api/workflows/{wf_id}/nodes", headers=h, json={"name":"N1","node_type":"llm_call","config":{},"position_x":100,"position_y":100}).json(); n2 = requests.post(f"{base}/api/workflows/{wf_id}/nodes", headers=h, json={"name":"N2","node_type":"llm_call","config":{},"position_x":300,"position_y":100}).json(); e = requests.post(f"{base}/api/workflows/{wf_id}/edges", headers=h, json={"source_node_id":n1["id"],"target_node_id":n2["id"]}).json(); print(f"Created edge: {n1['name']} → {n2['name']}"); print(f"Total edges: {len(requests.get(f'{base}/api/workflows/{wf_id}/edges', headers=h).json())}")
```

---

## 📊 Complete ETL Pipeline Example

```python
import requests

BASE = "http://localhost:8000"

# Login
token = requests.post(f"{BASE}/api/auth/login",
    json={"username":"alice","password":"secret123"}).json()["access_token"]
h = {"Authorization": f"Bearer {token}"}

# Create workflow
wf = requests.post(f"{BASE}/api/workflows", headers=h,
    json={"name":"ETL Pipeline"}).json()
wf_id = wf["id"]

# Create nodes
extract = requests.post(f"{BASE}/api/workflows/{wf_id}/nodes", headers=h,
    json={
        "name": "Extract Data",
        "node_type": "http_request",
        "config": {"method": "GET", "url": "https://api.example.com/data"},
        "position_x": 100, "position_y": 200
    }).json()

transform = requests.post(f"{BASE}/api/workflows/{wf_id}/nodes", headers=h,
    json={
        "name": "Transform",
        "node_type": "llm_call",
        "config": {"prompt_template": "Process: {input}"},
        "position_x": 300, "position_y": 200
    }).json()

load = requests.post(f"{BASE}/api/workflows/{wf_id}/nodes", headers=h,
    json={
        "name": "Load to DB",
        "node_type": "db_write",
        "config": {"table": "processed_data"},
        "position_x": 500, "position_y": 200
    }).json()

# Connect nodes
edge1 = requests.post(f"{BASE}/api/workflows/{wf_id}/edges", headers=h,
    json={"source_node_id": extract["id"], "target_node_id": transform["id"]}).json()

edge2 = requests.post(f"{BASE}/api/workflows/{wf_id}/edges", headers=h,
    json={"source_node_id": transform["id"], "target_node_id": load["id"]}).json()

# Verify
edges = requests.get(f"{BASE}/api/workflows/{wf_id}/edges", headers=h).json()

print("✅ Complete ETL Pipeline Created!")
print(f"   {extract['name']} → {transform['name']} → {load['name']}")
print(f"   Total edges: {len(edges)}")
```

---

## ✨ All Endpoints

```
✅ GET    /api/workflows/{wf_id}/edges           (List)
✅ POST   /api/workflows/{wf_id}/edges           (Create)
✅ GET    /api/workflows/{wf_id}/edges/{id}      (Get)
✅ DELETE /api/workflows/{wf_id}/edges/{id}      (Delete)
```

**All require authentication + workflow ownership!**

---

## 🎯 Success Criteria

- [x] Can create edges between nodes
- [x] Can list all edges
- [x] Can get specific edge
- [x] Can delete edge
- [x] Validates workflow ownership
- [x] Validates both nodes exist
- [x] Validates nodes belong to workflow
- [x] Proper error messages
- [x] Correct status codes

---

## 🚫 Error Examples

### 400: Invalid Node
```json
POST /api/workflows/{wf_id}/edges
{
  "source_node_id": "node-from-other-workflow",
  "target_node_id": "node-2-id"
}

→ 400 "Source node does not belong to this workflow"
```

### 404: Workflow Not Found
```json
GET /api/workflows/{wrong_wf_id}/edges

→ 404 "Workflow not found"
```

---

**Test now: http://localhost:8000/docs** 🚀

You can now build complete workflow graphs!





