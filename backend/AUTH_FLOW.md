# Authentication Flow Diagram

## 🔐 Complete Authentication Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT (Browser/Postman)                     │
└────────────┬────────────────────────────────────┬───────────────┘
             │                                    │
             │ 1. Register                        │ 3. Protected Request
             │ POST /api/auth/register            │ GET /api/auth/me
             │ {username, email, password}        │ Header: Bearer <token>
             │                                    │
             v                                    v
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Routes                          │
│                    (app/api/routes/auth.py)                     │
├─────────────────────────────────────────────────────────────────┤
│  register()              login()              get_current_user()│
│     │                      │                         │          │
│     v                      v                         v          │
│  Validate schema      Validate schema         Depends(...)      │
│  Call service         Call service            Extract token     │
└─────┬──────────────────────┬─────────────────────────┬──────────┘
      │                      │                         │
      │                      │                         │
      v                      v                         v
┌─────────────────────────────────────────────────────────────────┐
│                    Authentication Service                       │
│                  (app/services/auth_service.py)                 │
├─────────────────────────────────────────────────────────────────┤
│  register_user()      authenticate_user()    get_user_by_id()  │
│       │                     │                      │            │
│   Check duplicates     Verify password        Fetch from DB     │
│   Hash password        Check active           Return user       │
│   Save to DB           Return user                              │
└───────┬──────────────────────┬──────────────────────┬───────────┘
        │                      │                      │
        v                      v                      v
┌─────────────────────────────────────────────────────────────────┐
│                      Security Utilities                         │
│                    (app/core/security.py)                       │
├─────────────────────────────────────────────────────────────────┤
│  get_password_hash()  verify_password()  create_access_token()  │
│  decode_access_token()                                          │
│                                                                  │
│  • Bcrypt hashing                                               │
│  • JWT encoding/decoding                                        │
│  • Token expiration                                             │
└─────────────────────────────────────────────────────────────────┘
        │                      │                      │
        v                      v                      v
┌─────────────────────────────────────────────────────────────────┐
│                     PostgreSQL Database                         │
│                      (users table)                              │
├─────────────────────────────────────────────────────────────────┤
│  id | username | email | hashed_password | is_active | ...     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📝 Flow Details

### Flow 1: User Registration

```
1. Client → POST /api/auth/register
   Body: {username, email, password}
   
2. Route → Validate with Pydantic (UserCreate schema)
   
3. Route → Call AuthService.register_user()
   
4. Service → Check username exists?
   Query: SELECT * FROM users WHERE username = ?
   
5. Service → Check email exists?
   Query: SELECT * FROM users WHERE email = ?
   
6. Service → Hash password
   bcrypt.hash(password) → $2b$12$...
   
7. Service → Insert user
   INSERT INTO users (username, email, hashed_password)
   
8. Service → Return User object
   
9. Route → Convert to UserResponse (exclude password)
   
10. Client ← 201 Created
    {id, username, email, is_active, created_at}
```

### Flow 2: User Login

```
1. Client → POST /api/auth/login
   Body: {username, password}
   
2. Route → Validate with Pydantic (UserLogin schema)
   
3. Route → Call AuthService.authenticate_user()
   
4. Service → Fetch user by username
   Query: SELECT * FROM users WHERE username = ?
   
5. Service → Verify password
   bcrypt.verify(password, user.hashed_password)
   
6. Service → Check is_active = true
   
7. Service → Return User object (or None)
   
8. Route → Create JWT token
   JWT payload: {sub: user.id, exp: now + 30min}
   Sign with SECRET_KEY
   
9. Client ← 200 OK
   {access_token: "eyJhbGc...", token_type: "bearer"}
```

### Flow 3: Protected Request

```
1. Client → GET /api/auth/me
   Header: Authorization: Bearer eyJhbGc...
   
2. Middleware → Extract token from header
   OAuth2PasswordBearer extracts "eyJhbGc..."
   
3. Dependency → Call get_current_user()
   
4. Dependency → Decode JWT
   JWT.decode(token, SECRET_KEY)
   Extract user_id from payload["sub"]
   
5. Dependency → Call AuthService.get_user_by_id()
   Query: SELECT * FROM users WHERE id = ?
   
6. Dependency → Check user.is_active
   
7. Dependency → Return User object
   
8. Route → Receives current_user parameter
   
9. Client ← 200 OK
   {id, username, email, is_active, created_at}
```

---

## 🔑 Key Components

### 1. Password Security
```
Plain Password → bcrypt.hash() → $2b$12$xxxxxxxxxxxxxxxxxxxx...
                                   ↓
                            Stored in database
                                   ↓
Login: input → bcrypt.verify(input, stored_hash) → True/False
```

### 2. JWT Token Structure
```
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "sub": "user-uuid-here",
  "exp": 1234567890  # Unix timestamp
}

Signature:
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)

Final Token: xxxxx.yyyyy.zzzzz
```

### 3. Request Flow
```
Request
   ↓
Route Handler (validates schema)
   ↓
Service Layer (business logic)
   ↓
Database (async SQLAlchemy)
   ↓
Response (Pydantic model)
```

---

## 🛡️ Security Layers

```
┌─────────────────────────────────────────┐
│ Layer 1: Pydantic Validation           │
│ • Email format                          │
│ • Password length (6+ chars)            │
│ • Required fields                       │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ Layer 2: Business Logic Validation     │
│ • Duplicate username                    │
│ • Duplicate email                       │
│ • User exists                           │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ Layer 3: Password Security              │
│ • Bcrypt hashing (10 rounds)            │
│ • Automatic salt                        │
│ • Never store plain passwords           │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ Layer 4: JWT Security                   │
│ • Signed with SECRET_KEY                │
│ • 30-minute expiration                  │
│ • Token validation on each request      │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ Layer 5: Active User Check              │
│ • Only active users can authenticate    │
│ • Can deactivate without deletion       │
└─────────────────────────────────────────┘
```

---

## 🔄 State Transitions

```
New User Registration:
┌──────────┐  register   ┌──────────┐  login    ┌──────────┐
│  Guest   │ ────────→   │ Created  │ ────────→ │  Active  │
└──────────┘             └──────────┘           └──────────┘
                               │                       │
                               │ deactivate            │
                               v                       v
                         ┌──────────┐            ┌──────────┐
                         │ Inactive │ ←────────  │ Inactive │
                         └──────────┘ deactivate └──────────┘

Token Lifecycle:
┌──────────┐  login    ┌──────────┐  30 min   ┌──────────┐
│ No Token │ ────────→ │  Valid   │ ────────→ │ Expired  │
└──────────┘           └──────────┘           └──────────┘
                             │
                             │ logout / clear
                             v
                       ┌──────────┐
                       │ Cleared  │
                       └──────────┘
```

---

## 📊 Database Queries Used

```sql
-- 1. Check username exists (registration)
SELECT * FROM users WHERE username = 'alice';

-- 2. Check email exists (registration)
SELECT * FROM users WHERE email = 'alice@example.com';

-- 3. Insert new user (registration)
INSERT INTO users (id, username, email, hashed_password, is_active)
VALUES (gen_random_uuid(), 'alice', 'alice@example.com', '$2b$...', true);

-- 4. Fetch user for login (authentication)
SELECT * FROM users WHERE username = 'alice';

-- 5. Fetch user by ID (protected routes)
SELECT * FROM users WHERE id = '123e4567-e89b-12d3-a456-426614174000';
```

---

## 🎯 Usage Example

```python
# In a protected route
@router.post("/workflows")
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ← Magic happens here!
):
    # At this point:
    # 1. Token was validated
    # 2. User was fetched from database
    # 3. Active status was checked
    # 4. current_user is a full User object
    
    print(f"Creating workflow for user: {current_user.username}")
    print(f"User ID: {current_user.id}")
    print(f"User email: {current_user.email}")
    
    # Use current_user.id to link workflow to user
    workflow = await WorkflowService.create_workflow(
        db=db,
        user_id=current_user.id,
        workflow_data=workflow_data
    )
    
    return workflow
```

---

## 🚦 Error Handling

```
Registration Errors:
├─ 422: Validation error (invalid email, short password)
├─ 400: Username already registered
└─ 400: Email already registered

Login Errors:
├─ 422: Validation error (missing fields)
├─ 401: Incorrect username or password
└─ 401: User is inactive

Protected Route Errors:
├─ 401: No token provided
├─ 401: Invalid token
├─ 401: Expired token
├─ 401: User not found
└─ 403: Inactive user
```

---

**All flows are implemented and tested! 🎉**

