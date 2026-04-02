"""
PostgreSQL Authentication Fix Script
Fixes PostgreSQL authentication issues
"""
import psycopg2
from psycopg2 import sql
import os
import sys

def try_os_auth():
    """Try connecting using OS authentication"""
    print("Attempting OS user authentication...\n")
    
    try:
        # Try connecting without specifying user (uses OS username)
        conn = psycopg2.connect(
            host="localhost",
            database="postgres"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT current_user, version();")
        user, version = cursor.fetchone()
        print(f"✓ Connected as: {user}")
        print(f"  PostgreSQL: {version.split(',')[0]}")
        return conn
    except Exception as e:
        print(f"✗ OS auth failed: {str(e)[:100]}\n")
        return None

def reset_postgres_password(conn, new_password):
    """Reset postgres user password"""
    try:
        print(f"\nResetting postgres user password...\n")
        cursor = conn.cursor()
        
        # Reset password
        ALTER_QUERY = f"ALTER USER postgres WITH PASSWORD %s;"
        cursor.execute(ALTER_QUERY, (new_password,))
        conn.commit()
        
        cursor.close()
        return True, "Password reset successfully"
    except Exception as e:
        return False, str(e)

def create_phonepe_database(conn, db_user, db_password):
    """Create phonepe database and user"""
    try:
        print(f"\nCreating phonepe database and user...\n")
        cursor = conn.cursor()
        
        # Drop existing if exists (for re-running)
        cursor.execute("DROP DATABASE IF EXISTS phonepe;")
        cursor.execute("DROP USER IF EXISTS phonepe;")
        
        # Create new user
        CREATE_USER = f"CREATE USER {db_user} WITH PASSWORD %s;"
        cursor.execute(CREATE_USER, (db_password,))
        print(f"✓ User '{db_user}' created")
        
        # Create database
        cursor.execute("CREATE DATABASE phonepe OWNER phonepe;")
        print(f"✓ Database 'phonepe' created")
        
        # Grant privileges
        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE phonepe TO phonepe;")
        print(f"✓ Privileges granted")
        
        conn.commit()
        cursor.close()
        return True, "Database and user created successfully"
    except Exception as e:
        return False, str(e)

def test_new_connection(user, password, database):
    """Test connection with new credentials"""
    try:
        print(f"\nTesting connection with new credentials...\n")
        conn = psycopg2.connect(
            host="localhost",
            user=user,
            password=password,
            database=database,
            port=5432
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return True, f"Success! {version.split(',')[0]}"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("PostgreSQL Authentication Fix")
    print("=" * 70)
    print()
    
    # Step 1: Try to connect with OS auth
    print("STEP 1: Establishing admin connection...")
    print("-" * 70)
    admin_conn = try_os_auth()
    
    if not admin_conn:
        print("Could not establish admin connection.")
        print("Please check PostgreSQL installation and manually set credentials.\n")
        return False
    
    # Step 2: Reset postgres password
    print("\nSTEP 2: Resetting postgres user password...")
    print("-" * 70)
    new_password = "$antAbi1209"  # From .env
    success, msg = reset_postgres_password(admin_conn, new_password)
    
    if success:
        print(f"✓ {msg}")
    else:
        print(f"✗ Failed to reset password: {msg}")
        admin_conn.close()
        return False
    
    # Step 3: Create phonepe database and user
    print("\nSTEP 3: Creating phonepe database and user...")
    print("-" * 70)
    success, msg = create_phonepe_database(admin_conn, "phonepe", new_password)
    
    if success:
        print(f"✓ {msg}")
    else:
        print(f"✗ Failed: {msg}")
        admin_conn.close()
        return False
    
    admin_conn.close()
    
    # Step 4: Test with postgres user
    print("\nSTEP 4: Testing connection as postgres user...")
    print("-" * 70)
    success, msg = test_new_connection("postgres", new_password, "postgres")
    
    if success:
        print(f"✓ {msg}")
    else:
        print(f"✗ Failed: {msg}")
        return False
    
    # Step 5: Test with phonepe user
    print("\nSTEP 5: Testing connection as phonepe user...")
    print("-" * 70)
    success, msg = test_new_connection("phonepe", new_password, "phonepe")
    
    if success:
        print(f"✓ {msg}")
    else:
        print(f"✗ Failed: {msg}")
        return False
    
    # Step 6: Verification complete
    print("\n" + "=" * 70)
    print("✓ PostgreSQL Authentication Fixed!")
    print("=" * 70)
    print("\n.env file is already configured correctly:")
    print("  DB_HOST=localhost")
    print("  DB_USER=postgres")
    print(f"  DB_PASSWORD={new_password}")
    print("  DB_NAME=phonepe")
    print("  DB_PORT=5432")
    print("\nYou can now run:")
    print("  python src/database.py --full-setup")
    print("  streamlit run app/main.py")
    print()
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)
