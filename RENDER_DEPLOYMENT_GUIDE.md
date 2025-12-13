# Render Deployment Guide

Complete guide for deploying the AI Workflow Builder backend to Render.

---

## Prerequisites

- Render account (free tier works)
- PostgreSQL database on Render (or external PostgreSQL)
- Git repository with your code

---

## Step 1: Create PostgreSQL Database on Render

1. **Go to Render Dashboard** → New → PostgreSQL
2. **Configure:**
   - Name: `ai-workflow-builder-db` (or your choice)
   - Database: `ai_workflow_builder`
   - User: Auto-generated
   - Region: Choose closest to you
   - Plan: Free tier or paid
3. **Create Database**
4. **Save the connection string** - You'll need it for environment variables:
   - Format: `postgresql://user:password@hostname:port/database`
   - Convert to asyncpg format: `postgresql+asyncpg://user:password@hostname:port/database`

---

## Step 2: Create Web Service on Render

1. **Go to Render Dashboard** → New → Web Service
2. **Connect your repository** (GitHub, GitLab, etc.)

---

## Step 3: Configure Service Settings

### Basic Settings

- **Name:** `ai-workflow-builder-backend` (or your choice)
- **Region:** Choose closest to you
- **Branch:** `main` (or your default branch)
- **Root Directory:** Leave blank (root)
- **Runtime:** Docker

### Build & Deploy

- **Dockerfile Path:** `Dockerfile` (or leave blank - defaults to `./Dockerfile`)
- **Docker Build Context Directory:** `.` (or leave blank - defaults to root)
- **Docker Command:** Leave blank (uses Dockerfile CMD)
- **Pre-Deploy Command:** 
  ```bash
  cd /app && alembic upgrade head
  ```
- **Health Check Path:** `/health`
- **Auto-Deploy:** Enabled ✓

### Environment Variables

Add these environment variables in Render:

1. **DATABASE_URL**
   ```
   postgresql+asyncpg://user:password@hostname:port/database
   ```
   - Get this from your Render PostgreSQL service
   - Convert format: Add `+asyncpg` after `postgresql`
   - Example: `postgresql+asyncpg://postgres:abc123@dpg-xxx.render.com:5432/ai_workflow_builder`

2. **SECRET_KEY**
   ```
   (Generate a secure random key)
   ```
   - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - Important: Use a strong random string in production!

3. **ALGORITHM** (Optional - has default)
   ```
   HS256
   ```

4. **ACCESS_TOKEN_EXPIRE_MINUTES** (Optional - has default)
   ```
   30
   ```

5. **DEBUG** (Optional - set to False for production)
   ```
   False
   ```

6. **FAISS_INDEX_PATH** (Optional - has default)
   ```
   ./data/faiss
   ```

7. **MODEL_NAME** (Optional - has default)
   ```
   Qwen/Qwen2-0.5B-Instruct
   ```

8. **MODEL_DEVICE** (Optional - has default)
   ```
   cpu
   ```

### Build Filters (Optional)

**Ignored Paths:**
- `frontend/**` - Don't redeploy when frontend changes

**Included Paths:**
- Leave blank (defaults to all files) or add `backend/**` if you want to be explicit

---

## Step 4: Deploy

1. Click **Create Web Service**
2. Render will:
   - Build the Docker image
   - Run Pre-Deploy Command (migrations)
   - Start the service
   - Monitor health check endpoint

---

## Step 5: Verify Deployment

1. **Check Logs**
   - Go to your service → Logs
   - Look for: "Uvicorn running on http://0.0.0.0:PORT"

2. **Test Health Check**
   ```bash
   curl https://your-service-name.onrender.com/health
   ```
   Expected: `{"status":"healthy"}`

3. **Test API Docs**
   - Visit: `https://your-service-name.onrender.com/docs`
   - Should show Swagger UI

---

## Troubleshooting

### Error: ModuleNotFoundError: No module named 'app'

**Solution:** Ensure `ENV PYTHONPATH=/app` is in Dockerfile (already fixed)

### Error: No open ports detected

**Solution:** 
- Ensure server binds to `0.0.0.0` (not `localhost`)
- Use `${PORT:-8000}` for port binding
- Check that service exposes port correctly

### Error: Database connection failed

**Solutions:**
1. Check `DATABASE_URL` format - must be `postgresql+asyncpg://...`
2. Verify PostgreSQL service is running on Render
3. Check firewall/network settings
4. Ensure database exists

### Migration Errors

**Solution:**
- Check Pre-Deploy Command: `cd /app && alembic upgrade head`
- Verify `DATABASE_URL` is set correctly
- Check Alembic can find models (PYTHONPATH set)

### Port Binding Issues

**Solution:**
- Render provides `$PORT` environment variable
- Server must bind to: `0.0.0.0:$PORT`
- Dockerfile CMD uses: `${PORT:-8000}`

---

## Environment Variables Summary

### Required

```env
DATABASE_URL=postgresql+asyncpg://user:password@hostname:port/database
SECRET_KEY=your-secure-random-key-here
```

### Optional (with defaults)

```env
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=False
FAISS_INDEX_PATH=./data/faiss
MODEL_NAME=Qwen/Qwen2-0.5B-Instruct
MODEL_DEVICE=cpu
```

---

## Render Configuration Checklist

- [ ] PostgreSQL database created
- [ ] Web service created
- [ ] Dockerfile Path: `Dockerfile` (or blank)
- [ ] Docker Build Context: `.` (or blank)
- [ ] Pre-Deploy Command: `cd /app && alembic upgrade head`
- [ ] Health Check Path: `/health`
- [ ] Environment Variables:
  - [ ] `DATABASE_URL` set
  - [ ] `SECRET_KEY` set (strong random value)
  - [ ] `DEBUG=False` (production)
- [ ] Auto-Deploy enabled
- [ ] Service deployed successfully
- [ ] Health check passing
- [ ] API accessible at `/docs`

---

## Quick Reference

### Service URL Format
```
https://your-service-name.onrender.com
```

### Health Check
```
GET https://your-service-name.onrender.com/health
```

### API Documentation
```
https://your-service-name.onrender.com/docs
```

### Database Connection String Format
```
postgresql+asyncpg://username:password@hostname:port/database_name
```

---

**Last Updated:** December 3, 2025




