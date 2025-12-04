# PostgreSQL Setup Guide

This guide will help you set up PostgreSQL for the AI Workflow Builder backend.

## Option 1: Using Docker (Recommended - Easiest)

### Prerequisites
- Docker Desktop installed and running

### Steps

1. **Start Docker Desktop** (if not already running)

2. **Start PostgreSQL container:**
   ```bash
   docker-compose -f docker-compose.postgres.yml up -d
   ```

3. **Verify PostgreSQL is running:**
   ```bash
   docker ps
   ```
   You should see `ai-workflow-postgres` container running.

4. **Update your .env file** (if needed):
   The default configuration in `.env` should work:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_workflow_builder
   ```

5. **Run database setup script:**
   ```bash
   python scripts/setup_postgres.py
   ```

6. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

### Stopping PostgreSQL
```bash
docker-compose -f docker-compose.postgres.yml down
```

### Removing PostgreSQL (and all data)
```bash
docker-compose -f docker-compose.postgres.yml down -v
```

---

## Option 2: Local PostgreSQL Installation

### Windows Installation

1. **Download PostgreSQL:**
   - Visit: https://www.postgresql.org/download/windows/
   - Download and run the installer
   - During installation:
     - Set password for `postgres` user (remember this!)
     - Use default port: 5432
     - Keep default locale settings

2. **Verify Installation:**
   ```bash
   psql --version
   ```

3. **Update .env file:**
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/ai_workflow_builder
   ```
   Replace `YOUR_PASSWORD` with the password you set during installation.

4. **Create the database:**
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Create database
   CREATE DATABASE ai_workflow_builder;
   
   # Exit
   \q
   ```

5. **Run database setup script:**
   ```bash
   python scripts/setup_postgres.py
   ```

6. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

---

## Quick Setup (After PostgreSQL is Running)

Once PostgreSQL is accessible, run these commands:

```bash
# 1. Test connection and create database (if needed)
python scripts/setup_postgres.py

# 2. Run migrations to create tables
alembic upgrade head

# 3. (Optional) Create a test user
python scripts/create_test_user.py

# 4. Start the server
uvicorn app.main:app --reload
```

---

## Troubleshooting

### Connection Refused
- **Docker**: Make sure Docker Desktop is running
- **Local**: Make sure PostgreSQL service is running
  - Windows: Check Services app for "postgresql-x64-*" service

### Authentication Failed
- Check username and password in `.env` file
- For Docker: Default is `postgres:postgres`
- For local install: Use the password you set during installation

### Database Already Exists
- That's fine! The setup script will detect it and skip creation
- You can proceed directly to migrations

### Port 5432 Already in Use
- Another PostgreSQL instance might be running
- Check what's using the port: `netstat -ano | findstr :5432`
- Or change the port in docker-compose.yml and update .env

---

## Default Configuration

- **Host:** localhost
- **Port:** 5432
- **Database:** ai_workflow_builder
- **Username:** postgres
- **Password:** postgres (Docker) / your installation password (Local)

Update these in your `.env` file as needed.

