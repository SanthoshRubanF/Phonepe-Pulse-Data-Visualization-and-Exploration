# PostgreSQL Database Setup Guide

This guide explains how to set up and use PostgreSQL database with the PhonePe Pulse dashboard.

## Prerequisites

- PostgreSQL 12+ installed and running
- psycopg2-binary (included in `requirements.txt`)
- Python 3.8+

## Quick Start

### 1. Install Database Driver
```bash
pip install -r requirements.txt
```

This installs `psycopg2-binary` which enables PostgreSQL connectivity.

### 2. Configure Database Connection

Edit `.env` file:
```env
# Database Configuration
DB_HOST=localhost          # PostgreSQL server address
DB_USER=postgres           # Database user (default is 'postgres')
DB_PASSWORD=your_password  # Your PostgreSQL password
DB_NAME=phonepe            # Database name
DB_PORT=5432               # PostgreSQL port (default is 5432)

# Data Configuration
DATA_BASE_PATH=./pulse/data
```

### 3. Create Database

If the database doesn't exist, create it in PostgreSQL:
```bash
# Using psql command line
psql -U postgres -c "CREATE DATABASE phonepe;"

# Or using a PostgreSQL client:
# Connect to PostgreSQL and run:
# CREATE DATABASE phonepe;
```

### 4. Setup Database Tables

Run the database setup script:
```bash
# Test connection
python src/database.py --test

# Create tables
python src/database.py --setup

# Or do both at once
python src/database.py --test --setup
```

### 5. Sync JSON Data to Database

```bash
python src/database.py --sync
```

This will:
- Load all PhonePe Pulse JSON files
- Create/recreate tables
- Insert data into PostgreSQL

### 6. Full Setup in One Command

```bash
python src/database.py --full-setup
```

This combines: test connection → create tables → sync data

## Database Management

### Check Database Status

```bash
python src/database.py --stats
```

Shows row counts for each table:
- transactions
- insurance
- users

### Clear Database

```bash
python src/database.py --clear
```

**Warning**: This deletes all data. Confirmation required.

### View Database in Dashboard

The dashboard automatically uses the database if available. If the database is unavailable, it automatically falls back to loading from JSON files.

## Using Database in Code

### Load Data from Database

```python
from src.data_loader import DataLoader

loader = DataLoader()

# Load from database (with automatic fallback to JSON if DB unavailable)
transactions = loader.load_from_database('transaction')
insurance = loader.load_from_database('insurance')
users = loader.load_from_database('user')
```

### Direct Database Connection

```python
from src.data_loader import DataLoader

loader = DataLoader()
conn = loader.get_db_connection()

if conn:
    cursor = conn.cursor()
    # Your custom SQL queries here
    cursor.close()
```

### Database Manager Class

```python
from src.database import DatabaseManager

manager = DatabaseManager()

# Test connection
if manager.test_connection():
    print("Database is connected!")

# Setup database
manager.setup_database()

# Sync data
manager.sync_data()

# Get statistics
stats = manager.get_database_stats()
print(f"Total transactions: {stats['transactions']}")
```

## Database Schema

### transactions table
```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    state VARCHAR(100),
    year INTEGER,
    quarter INTEGER,
    transaction_type VARCHAR(100),
    transaction_count BIGINT,
    transaction_amount BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Indexes:
- `idx_transactions_state_year` on (state, year)
- `idx_transactions_year_quarter` on (year, quarter)

### insurance table
```sql
CREATE TABLE insurance (
    id SERIAL PRIMARY KEY,
    state VARCHAR(100),
    year INTEGER,
    quarter INTEGER,
    insurance_type VARCHAR(100),
    insurance_count BIGINT,
    insurance_amount BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Indexes:
- `idx_insurance_state_year` on (state, year)
- `idx_insurance_year_quarter` on (year, quarter)

### users table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    state VARCHAR(100),
    year INTEGER,
    quarter INTEGER,
    brands VARCHAR(100),
    user_count BIGINT,
    percentage REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Indexes:
- `idx_users_state_year` on (state, year)
- `idx_users_year_quarter` on (year, quarter)

## Troubleshooting

### Connection Failed
```
Error: PostgreSQL connection refused
```
**Solution:**
1. Verify PostgreSQL is running: `pg_isready -h localhost -p 5432`
2. Check credentials in `.env` file
3. Ensure database exists: `psql -U postgres -c "SELECT datname FROM pg_database;"`

### Authentication Failed
```
Error: FATAL: Ident authentication failed
```
**Solution:**
1. Check PostgreSQL `pg_hba.conf` configuration
2. Ensure user has correct password
3. Try connecting with psql first: `psql -U postgres -h localhost`

### Database Not Found
```
Error: database "phonepe" does not exist
```
**Solution:**
Create the database:
```bash
psql -U postgres -c "CREATE DATABASE phonepe;"
```

### psycopg2 Not Installed
```
Error: No module named 'psycopg2'
```
**Solution:**
```bash
pip install psycopg2-binary
```

### Sync Takes Too Long
- First sync from JSON to database takes time (depends on data size)
- Subsequent loads from database are much faster
- Syncing is a one-time operation per database update

## Performance Tips

1. **Indexes**: Created automatically for faster queries
2. **Caching**: DataLoader caches results in memory
3. **Batch Operations**: Data inserted in batches of 1000 rows
4. **UNIQUE Constraints**: Prevents duplicate data

## Example: Running Dashboard with Database

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Setup database (one-time)
python src/database.py --full-setup

# Run dashboard
streamlit run app/main.py
```

The dashboard will now load data from PostgreSQL instead of JSON files.

## Backup and Recovery

### Backup Database
```bash
pg_dump -U postgres -d phonepe > phonepe_backup.sql
```

### Restore Database
```bash
psql -U postgres -d phonepe < phonepe_backup.sql
```

## Optional: Use Different PostgreSQL Server

To use a remote PostgreSQL server:

1. Edit `.env`:
```env
DB_HOST=remote-server.example.com
DB_USER=username
DB_PASSWORD=password
DB_NAME=phonepe
DB_PORT=5432
```

2. Ensure network access is allowed
3. Test connection: `python src/database.py --test`

## Switching Between JSON and Database

The DataLoader automatically:
- **Prefers database** if connection is available
- **Falls back to JSON** if database is unavailable
- **Caches results** for performance

To force JSON loading (if needed):
```python
from src.data_loader import DataLoader

loader = DataLoader()

# Always load from JSON
df = loader.load_from_json('aggregated', 'transaction')
```

To force database loading:
```python
# Always load from database (with fallback to JSON on error)
df = loader.load_from_database('transaction')
```

## Next Steps

1. Configure PostgreSQL in `.env`
2. Run: `python src/database.py --full-setup`
3. Start dashboard: `streamlit run app/main.py`
4. Data will now be served from PostgreSQL

For issues or questions, check the troubleshooting section above.
