# Backend Setup Instructions

## 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Setup Environment Variables

```bash
# Copy example env file
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env with your database credentials
# Update DATABASE_URL with your PostgreSQL connection string
```

## 4. Setup PostgreSQL Database

Make sure PostgreSQL is running and create a database:

```sql
CREATE DATABASE ai_workflow_builder;
```

## 5. Run Database Migrations

```bash
# Generate initial migration (if not already exists)
alembic revision --autogenerate -m "initial_migration"

# Apply migrations
alembic upgrade head
```

## 6. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- Main API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Module not found errors
Make sure virtual environment is activated and dependencies are installed.

### Database connection errors
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure database exists

### Alembic errors
- Make sure you're in the backend directory
- Check alembic.ini configuration
- Verify app.db.base imports all models


