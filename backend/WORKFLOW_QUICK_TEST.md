# Workflow CRUD - Quick Test Guide

## 🚀 5-Minute Test

### Step 1: Start Server
```bash
cd backend
uvicorn app.main:app --reload
```

### Step 2: Open Swagger
http://localhost:8000/docs

### Step 3: Register & Login
```json
POST /api/auth/register
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "secret123"
}

POST /api/auth/login
{
  "username": "alice",
  "password": "secret123"
}
```
*Copy the access_token*

### Step 4: Authorize in Swagger
- Click "Authorize" button (top right)
- Paste token
- Click "Authorize"

### Step 5: Test Workflow CRUD

#### Create
```json
POST /api/workflows
{
  "name": "My Workflow",
  "description": "Test workflow"
}
```
*Copy the workflow id from response*

#### List
```
GET /api/workflows
```

#### Get
```
GET /api/workflows/{workflow_id}
```

#### Update
```json
PUT /api/workflows/{workflow_id}
{
  "name": "Updated Name"
}
```

#### Delete
```
DELETE /api/workflows/{workflow_id}
```

---

## ✅ What Should Happen

| Test | Expected Result |
|------|----------------|
| Create | 201 Created with workflow object |
| List | 200 OK with array of workflows |
| Get | 200 OK with workflow object |
| Update | 200 OK with updated workflow |
| Delete | 204 No Content (empty body) |

---

## 🔐 Authorization Tests

### Test 1: User Isolation
1. Register user "alice"
2. Create workflow as alice
3. Register user "bob"
4. Try to get alice's workflow as bob
5. **Result:** 404 Not Found ✅

### Test 2: List Filtering
1. Register user "alice"
2. Create 2 workflows as alice
3. Register user "bob"
4. Create 1 workflow as bob
5. List workflows as alice
6. **Result:** See only alice's 2 workflows ✅

---

## 🧪 Python One-Liner Test

```python
import requests; base = "http://localhost:8000"; r = requests.post(f"{base}/api/auth/register", json={"username":"test","email":"test@test.com","password":"test123"}); token = requests.post(f"{base}/api/auth/login", json={"username":"test","password":"test123"}).json()["access_token"]; h = {"Authorization": f"Bearer {token}"}; wf = requests.post(f"{base}/api/workflows", headers=h, json={"name":"Test","description":"Test WF"}).json(); print("Created:", wf["id"]); print("List:", len(requests.get(f"{base}/api/workflows", headers=h).json())); requests.put(f"{base}/api/workflows/{wf['id']}", headers=h, json={"name":"Updated"}); print("Updated:", requests.get(f"{base}/api/workflows/{wf['id']}", headers=h).json()["name"]); print("Delete:", requests.delete(f"{base}/api/workflows/{wf['id']}", headers=h).status_code)
```

---

## 📊 Expected Responses

### Create (201)
```json
{
  "id": "uuid",
  "user_id": "user-uuid",
  "name": "My Workflow",
  "description": "Test workflow",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### List (200)
```json
[
  {
    "id": "uuid-1",
    "name": "Workflow 1",
    ...
  },
  {
    "id": "uuid-2",
    "name": "Workflow 2",
    ...
  }
]
```

### Get (200)
```json
{
  "id": "uuid",
  "name": "My Workflow",
  ...
}
```

### Update (200)
```json
{
  "id": "uuid",
  "name": "Updated Name",
  "updated_at": "2024-01-01T12:00:00"  ← Changed
}
```

### Delete (204)
```
(Empty response body)
```

---

## 🐛 Error Responses

### 404 Not Found
```json
{
  "detail": "Workflow not found"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## ✨ All Endpoints

```
✅ GET    /api/workflows              (List)
✅ POST   /api/workflows              (Create)
✅ GET    /api/workflows/{id}         (Get)
✅ PUT    /api/workflows/{id}         (Update)
✅ DELETE /api/workflows/{id}         (Delete)
```

**All require authentication!**

---

## 🎯 Success Criteria

- [x] Can create workflow
- [x] Can list workflows
- [x] Can get specific workflow
- [x] Can update workflow
- [x] Can delete workflow
- [x] Users see only their workflows
- [x] Proper error messages
- [x] Correct status codes

---

**Test now: http://localhost:8000/docs** 🚀

