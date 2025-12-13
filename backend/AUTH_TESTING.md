# Authentication Testing Guide

## ✅ What Was Implemented

### Files Updated:

1. **`app/services/auth_service.py`** - Complete authentication service with:

   - User registration with duplicate checking
   - Password verification
   - User retrieval by ID, username, email
   - Proper async SQLAlchemy queries

2. **`app/api/routes/auth.py`** - Complete route handlers:

   - POST `/api/auth/register` - Register new users
   - POST `/api/auth/login` - Login and get JWT token
   - GET `/api/auth/me` - Get current user info

3. **`app/core/dependencies.py`** - Complete JWT authentication:

   - Token validation
   - User fetching from database
   - Active user checking

4. **`app/core/security.py`** - Already complete:
   - Password hashing with bcrypt
   - JWT token creation/decoding

## 🚀 Quick Test

### 1. Start the Server

```bash
cd backend
# Make sure venv is activated and dependencies installed
uvicorn app.main:app --reload
```

### 2. Visit Swagger UI

Open: http://localhost:8000/docs

## 📝 Manual Testing Steps

### Test 1: Register a New User

**Endpoint:** `POST /api/auth/register`

**Request Body:**

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

**Expected Response (201 Created):**

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "id": "uuid-here",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

**Error Cases:**

- Duplicate username → 400 "Username already registered"
- Duplicate email → 400 "Email already registered"
- Invalid email format → 422 Validation error
- Password too short (< 6 chars) → 422 Validation error

### Test 2: Login with Credentials

**Endpoint:** `POST /api/auth/login`

**Request Body:**

```json
{
  "username": "testuser",
  "password": "password123"
}
```

**Expected Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Cases:**

- Wrong username → 401 "Incorrect username or password"
- Wrong password → 401 "Incorrect username or password"
- Inactive user → 401 "Incorrect username or password"

### Test 3: Get Current User Info

**Endpoint:** `GET /api/auth/me`

**Headers:**

```
Authorization: Bearer <your-access-token-here>
```

**Expected Response (200 OK):**

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "id": "uuid-here",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

**Error Cases:**

- No token → 401 "Not authenticated"
- Invalid token → 401 "Could not validate credentials"
- Expired token → 401 "Could not validate credentials"

## 🧪 Using cURL

### Register

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### Get Current User (replace TOKEN with actual token)

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer TOKEN"
```

## 🐍 Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Register
response = requests.post(
    f"{BASE_URL}/api/auth/register",
    json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
)
print("Register:", response.status_code, response.json())

# 2. Login
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={
        "username": "testuser",
        "password": "password123"
    }
)
token_data = response.json()
token = token_data["access_token"]
print("Login:", response.status_code, token)

# 3. Get current user
response = requests.get(
    f"{BASE_URL}/api/auth/me",
    headers={"Authorization": f"Bearer {token}"}
)
print("Me:", response.status_code, response.json())
```

## 🔍 What's Happening Under the Hood

### Registration Flow:

1. Route receives UserCreate schema
2. Service checks for duplicate username/email
3. Password is hashed with bcrypt
4. User saved to database with UUID
5. User object returned (password excluded by Pydantic)

### Login Flow:

1. Route receives username + password
2. Service fetches user by username
3. Password verified against hashed password
4. JWT token created with user ID in payload
5. Token returned with 30-min expiration

### Get Current User Flow:

1. Token extracted from Authorization header
2. JWT decoded and validated
3. User ID extracted from token payload
4. User fetched from database by ID
5. Active status checked
6. User object returned

## 🔐 Security Features Implemented

✅ **Password Hashing** - Bcrypt with salt
✅ **JWT Tokens** - HS256 algorithm
✅ **Token Expiration** - 30 minutes (configurable)
✅ **Duplicate Prevention** - Username and email uniqueness
✅ **Active User Check** - Inactive users can't authenticate
✅ **Async Operations** - All database calls are non-blocking
✅ **Type Safety** - Full Pydantic validation

## 📊 Database Verification

Check the database directly:

```sql
-- View created users
SELECT id, username, email, is_active, created_at
FROM users;

-- Verify password is hashed (should see bcrypt hash)
SELECT username, hashed_password
FROM users;
```

## 🐛 Troubleshooting

### "Could not validate credentials"

- Token might be expired (30 min default)
- Token might be malformed
- User might have been deleted

### "Username already registered"

- User with that username exists in database
- Try a different username

### Module import errors

- Make sure you're in backend/ directory
- Virtual environment activated
- Dependencies installed

### Database connection errors

- PostgreSQL running?
- DATABASE_URL correct in .env?
- Migrations applied? (`alembic upgrade head`)

## ✨ Next Steps

Now that authentication works, you can:

1. Protect other routes with `Depends(get_current_user)`
2. Implement workflow CRUD operations
3. Add user-specific workflow filtering
4. Build the execution engine

Example of protecting a route:

```python
@router.post("/workflows")
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ← Protected!
):
    # Only authenticated users can reach here
    # current_user is the User object
    pass
```

---

**Authentication is fully functional! 🎉**




