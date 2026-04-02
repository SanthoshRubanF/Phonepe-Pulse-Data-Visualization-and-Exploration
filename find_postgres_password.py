"""
PostgreSQL Password Guesser
Tries common default PostgreSQL passwords
"""
import psycopg2

def try_password(user, password, database="postgres"):
    """Try a single password"""
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",  # Use IPv4 explicitly
            user=user,
            password=password,
            database=database,
            port=5432,
            connect_timeout=3
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return True, version
    except psycopg2.OperationalError:
        return False, None
    except psycopg2.DatabaseError:
        return False, None

print("=" * 70)
print("PostgreSQL Default Password Finder")
print("=" * 70)
print("\nTrying common PostgreSQL default passwords...\n")

common_passwords = [
    "",                      # Empty password
    "postgres",             # Most common
    "password",             # Generic
    "admin",                # Admin
    "12345",                # Numeric
    "123456",               # Numeric
    "1234",                 # Numeric
    "root",                 # Root
    "postgres123",          # Postgres + number
    "postgrespass",         # Postgres + pass
    "changeme",             # Default for some
    "P@ssw0rd",            # Password pattern
    "P@ssword123",         # Password pattern
]

found = False
for password in common_passwords:
    display_pwd = f"'{password}'" if password else "(empty)"
    success, version = try_password("postgres", password)
    
    if success:
        print(f"✓ SUCCESS with password: {display_pwd}")
        print(f"  PostgreSQL: {version.split(',')[0]}\n")
        found = True
        
        # Save to file
        with open("postgres_credentials.txt", "w") as f:
            f.write(f"username: postgres\n")
            f.write(f"password: {password}\n")
            f.write(f"host: localhost\n")
            f.write(f"port: 5432\n")
        print("✓ Credentials saved to postgres_credentials.txt\n")
        break
    else:
        print(f"✗ Failed with: {display_pwd}")

if not found:
    print("\n" + "=" * 70)
    print("✗ None of the common passwords worked.")
    print("=" * 70)
    print("\nOptions:")
    print("1. Check what password PostgreSQL was installed with")
    print("2. Use PostgreSQL pgAdmin GUI to reset password")
    print("3. Modify pg_hba.conf to use 'trust' authentication (not secure)")
    print("4. Reinstall PostgreSQL with known password")
    print("\nTo reinstall PostgreSQL:")
    print("  1. Uninstall PostgreSQL")
    print("  2. Reinstall and set password='$antAbi1209' during setup")
