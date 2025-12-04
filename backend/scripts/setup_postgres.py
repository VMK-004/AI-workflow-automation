"""Script to test PostgreSQL connection and create database if needed"""
import asyncio
import asyncpg
import sys
import os

# Add parent directory to path to import settings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings

async def test_connection_and_create_db():
    """Test PostgreSQL connection and create database if it doesn't exist"""
    
    # Parse the DATABASE_URL to get connection details
    db_url = settings.DATABASE_URL
    
    if not db_url.startswith("postgresql"):
        print(f"⚠️  DATABASE_URL is not PostgreSQL: {db_url}")
        return False
    
    # Extract connection details
    # Format: postgresql+asyncpg://user:password@host:port/database
    try:
        # Parse the URL
        url_parts = db_url.replace("postgresql+asyncpg://", "").split("/")
        auth_host_port = url_parts[0]
        database_name = url_parts[1] if len(url_parts) > 1 else "postgres"
        
        auth, host_port = auth_host_port.split("@")
        user, password = auth.split(":")
        host, port = host_port.split(":") if ":" in host_port else (host_port, "5432")
        
        print(f"🔍 Testing PostgreSQL connection...")
        print(f"   Host: {host}:{port}")
        print(f"   User: {user}")
        print(f"   Target Database: {database_name}")
        
        # Try to connect to postgres database first (to check if server is running)
        try:
            admin_conn = await asyncpg.connect(
                host=host,
                port=int(port),
                user=user,
                password=password,
                database="postgres"
            )
            print("✓ Connected to PostgreSQL server")
            
            # Check if target database exists
            db_exists = await admin_conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1",
                database_name
            )
            
            if db_exists:
                print(f"✓ Database '{database_name}' already exists")
                await admin_conn.close()
                return True
            else:
                print(f"📝 Creating database '{database_name}'...")
                await admin_conn.execute(f'CREATE DATABASE "{database_name}"')
                print(f"✓ Database '{database_name}' created successfully")
                await admin_conn.close()
                return True
                
        except asyncpg.InvalidPasswordError:
            print(f"✗ Authentication failed: Invalid password for user '{user}'")
            print(f"  Please check your DATABASE_URL in .env file")
            return False
        except asyncpg.InvalidCatalogNameError:
            print(f"✗ Cannot connect to PostgreSQL server")
            print(f"  Please ensure PostgreSQL is running on {host}:{port}")
            return False
        except Exception as e:
            print(f"✗ Connection error: {e}")
            print(f"  Please check:")
            print(f"    1. PostgreSQL is installed and running")
            print(f"    2. DATABASE_URL in .env file is correct")
            print(f"    3. User '{user}' has proper permissions")
            return False
            
    except Exception as e:
        print(f"✗ Error parsing DATABASE_URL: {e}")
        print(f"  Current DATABASE_URL: {db_url}")
        print(f"  Expected format: postgresql+asyncpg://user:password@host:port/database")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection_and_create_db())
    sys.exit(0 if success else 1)

