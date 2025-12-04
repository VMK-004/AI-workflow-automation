# Render Deployment Configuration - Quick Reference

## ✅ Fixed Issues

1. **Module Import Error** - Added `ENV PYTHONPATH=/app` to Dockerfile
2. **Port Binding** - Updated to use `${PORT:-8000}` for Render compatibility
3. **Migration Separation** - Moved migrations to Pre-Deploy Command

---

## 📋 Render Service Configuration

### Basic Settings
- **Name:** `ai-workflow-builder-backend`
- **Region:** Your choice
- **Branch:** `main`
- **Root Directory:** (blank - uses root)
- **Runtime:** Docker

### Build Settings

- **Dockerfile Path:** `Dockerfile`
- **Docker Build Context Directory:** `.` (or leave blank)
- **Docker Command:** (leave blank)
- **Pre-Deploy Command:**
  ```
  cd /app && alembic upgrade head
  ```
- **Health Check Path:** `/health`
- **Auto-Deploy:** ✓ Enabled

### Build Filters

**Ignored Paths:**
- `frontend/**`

**Included Paths:**
- (leave blank - defaults to all)

---

## 🔐 Environment Variables (Set in Render)

### Required

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
SECRET_KEY=your-secure-random-key-here
```

### Optional (Recommended for Production)

```env
DEBUG=False
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Optional (Has Defaults)

```env
FAISS_INDEX_PATH=./data/faiss
MODEL_NAME=Qwen/Qwen2-0.5B-Instruct
MODEL_DEVICE=cpu
```

---

## 🚀 Quick Start Steps

1. Create PostgreSQL database on Render
2. Copy the Internal Database URL
3. Convert format: Add `+asyncpg` after `postgresql`
   - Example: `postgresql://...` → `postgresql+asyncpg://...`
4. Create Web Service
5. Use settings above
6. Set environment variables
7. Deploy!

---

**The Dockerfile has been fixed and is ready for Render deployment!**

