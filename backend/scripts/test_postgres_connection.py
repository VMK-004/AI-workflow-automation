"""Test PostgreSQL connection from application"""
import asyncio
from app.db.database import engine

async def test_connection():
    """Test database connection"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1 as test")
            row = result.fetchone()
            if row and row[0] == 1:
                print("✓ Database connection successful")
                return True
            else:
                print("✗ Connection test failed")
                return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)




