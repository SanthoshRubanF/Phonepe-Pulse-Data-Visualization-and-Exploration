"""
Reset PostgreSQL Password using Trust Authentication
"""
import psycopg2
import sys

print("=" * 70)
print("PostgreSQL Password Reset")
print("=" * 70)
print("\nAttempting to connect with trust authentication...\n")

try:
    # Try connecting without password (trust auth)
    conn = psycopg2.connect(
        host="127.0.0.1",
        user="postgres",
        database="postgres",
        port=5432,
        connect_timeout=5
    )
    
    # Enable autocommit for DDL commands
    conn.autocommit = True
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✓ Connected to PostgreSQL")
    print(f"  {version.split(',')[0]}\n")
    
    # Reset password
    new_password = "$antAbi1209"
    print(f"Resetting postgres user password...\n")
    cursor.execute("ALTER USER postgres WITH PASSWORD %s;", (new_password,))
    print(f"✓ Password reset to: {new_password}\n")
    
    # Create phonepe database
    print(f"Creating phonepe database...\n")
    
    # Terminate other connections to phonepe database
    cursor.execute("""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = 'phonepe'
        AND pid <> pg_backend_pid();
    """)
    
    # Now drop and create the database
    cursor.execute("DROP DATABASE IF EXISTS phonepe;")
    cursor.execute("CREATE DATABASE phonepe;")
    print(f"✓ Database 'phonepe' created\n")
    
    cursor.close()
    conn.close()
    
    # Test new credentials
    print("Testing connection with new password...\n")
    test_conn = psycopg2.connect(
        host="127.0.0.1",
        user="postgres",
        password=new_password,
        database="postgres",
        port=5432,
        connect_timeout=5
    )
    test_cursor = test_conn.cursor()
    test_cursor.execute("SELECT version();")
    test_version = test_cursor.fetchone()[0]
    test_cursor.close()
    test_conn.close()
    
    print(f"✓ Successfully connected with new password\n")
    
    print("=" * 70)
    print("✓ PostgreSQL Authentication Fixed Successfully!")
    print("=" * 70)
    print("\n.env is configured with:")
    print("  DB_USER=postgres")
    print(f"  DB_PASSWORD={new_password}")
    print("\nYou can now run:")
    print("  python src/database.py --full-setup")
    print("  streamlit run app/main.py")
    print()

except psycopg2.OperationalError as e:
    print(f"✗ Connection failed: {str(e)[:100]}")
    print("\nNote: pg_hba.conf may require administrative restart.")
    print("Try restarting PostgreSQL manually through Windows Services.")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {str(e)}")
    sys.exit(1)
