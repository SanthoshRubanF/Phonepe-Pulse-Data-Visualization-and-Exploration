"""
PostgreSQL Authentication Troubleshooter
Helps identify and fix PostgreSQL authentication issues
"""
import psycopg2
from psycopg2 import sql

def test_connection(host, user, password, database="postgres", port=5432):
    """Test a database connection"""
    try:
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return True, version
    except psycopg2.OperationalError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def try_different_credentials():
    """Try connecting with different credential combinations"""
    print("=" * 70)
    print("PostgreSQL Authentication Troubleshooter")
    print("=" * 70)
    print("\nAttempting connections with different credentials...\n")
    
    credentials = [
        ("localhost", "postgres", "", "postgres", 5432),
        ("localhost", "postgres", "postgres", "postgres", 5432),
        ("localhost", "postgres", "password", "postgres", 5432),
        ("127.0.0.1", "postgres", "", "postgres", 5432),
        ("127.0.0.1", "postgres", "postgres", "postgres", 5432),
    ]
    
    results = []
    for host, user, password, database, port in credentials:
        cred_string = f"user={user}, password={'(empty)' if not password else '***'}, host={host}"
        success, msg = test_connection(host, user, password, database, port)
        results.append((cred_string, success, msg))
        
        if success:
            print(f"✓ SUCCESS with: {cred_string}")
            print(f"  PostgreSQL: {msg}")
        else:
            print(f"✗ Failed: {cred_string}")
            # Print first line of error only
            error_line = str(msg).split('\n')[0]
            print(f"  Error: {error_line[:70]}")
    
    # Show summary
    print("\n" + "=" * 70)
    successful = [r for r in results if r[1]]
    if successful:
        print(f"\n✓ Found {len(successful)} working connection(s):\n")
        for cred, _, msg in successful:
            print(f"  {cred}")
    else:
        print("\n✗ No working connections found.")
        print("\nPostgreSQL appears to not be running or is not accessible.")
        print("\nOptions:")
        print("1. Start PostgreSQL service (Windows Service, Docker, etc.)")
        print("2. Check if PostgreSQL is installed")
        print("3. Verify firewall allows localhost:5432")

if __name__ == "__main__":
    try_different_credentials()
