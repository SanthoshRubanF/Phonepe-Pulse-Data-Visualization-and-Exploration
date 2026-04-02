"""
PostgreSQL Database Usage Examples for PhonePe Pulse Dashboard
"""

# Example 1: Basic Database Manager Usage
# ==========================================

from src.database import DatabaseManager

manager = DatabaseManager()

# Test connection
if manager.test_connection():
    print("✓ Database connected!")

# Setup tables (one-time)
manager.setup_database()

# Sync data
manager.sync_data()

# Get statistics
stats = manager.get_database_stats()
print(f"Database has {stats['transactions']} transaction records")


# Example 2: Load Data from Database in Python
# ============================================

from src.data_loader import DataLoader
import pandas as pd

loader = DataLoader()

# Load data from database (auto-fallback to JSON if unavailable)
transactions = loader.load_from_database('transaction')
insurance = loader.load_from_database('insurance')
users = loader.load_from_database('user')

# Use the data
print(f"Loaded {len(transactions)} transaction records")
print(transactions.head())


# Example 3: Direct Database Connection and Custom Queries
# ========================================================

from src.data_loader import DataLoader

loader = DataLoader()
conn = loader.get_db_connection()

if conn:
    cursor = conn.cursor()
    
    # Run custom query
    cursor.execute("""
        SELECT states, year, SUM(transaction_amount) as total_amount
        FROM transactions
        GROUP BY state, year
        ORDER BY year DESC
    """)
    
    results = cursor.fetchall()
    for row in results:
        state, year, amount = row
        print(f"{state} ({year}): ₹{amount:,}")
    
    cursor.close()


# Example 4: Use in Streamlit Dashboard
# =====================================

import streamlit as st
from src.data_loader import DataLoader

st.title("PhonePe Pulse Dashboard")

# Data will auto-load from database or JSON
loader = DataLoader()
transactions = loader.load_from_database('transaction')

# Display data
st.dataframe(transactions)

# Show stats
st.metric(
    label="Total Transactions",
    value=len(transactions),
    delta=None
)


# Example 5: Database Management via Command Line
# ===============================================

"""
# Test connection
python src/database.py --test

# Create tables
python src/database.py --setup

# Sync JSON data
python src/database.py --sync

# View statistics
python src/database.py --stats

# Full setup (test → create → sync)
python src/database.py --full-setup

# Clear database
python src/database.py --clear
"""


# Example 6: Complete Setup Script
# ================================

from src.database import DatabaseManager

manager = DatabaseManager()

# Step 1: Test
print("Testing database connection...")
if not manager.test_connection():
    print("Database not available!")
    exit(1)

# Step 2: Setup
print("Setting up database...")
manager.setup_database()

# Step 3: Sync
print("Syncing data...")
manager.sync_data()

# Step 4: Verify
stats = manager.get_database_stats()
print(f"✓ Setup complete! Database has {sum(stats.values())} total records")


# Example 7: Handling Database Unavailability
# ==========================================

from src.data_loader import DataLoader

loader = DataLoader()

# Try database first
try:
    data = loader.load_from_database('transaction')
    print(f"Loaded from database: {len(data)} records")
except Exception as e:
    print(f"Database error, using JSON: {e}")
    data = loader.load_from_json('aggregated', 'transaction')
    print(f"Loaded from JSON: {len(data)} records")


# Example 8: Performance Comparison
# ================================

import time
from src.data_loader import DataLoader

loader = DataLoader()

# First call (creates cache)
start = time.time()
data1 = loader.load_from_database('transaction')
time1 = time.time() - start

# Second call (from cache)
start = time.time()
data2 = loader.load_from_database('transaction')
time2 = time.time() - start

print(f"First load: {time1:.2f}s")
print(f"Second load (cached): {time2:.2f}s")
print(f"Speedup: {time1/time2:.1f}x")


# Example 9: Interactive Database Setup
# ====================================

import logging
from src.database import DatabaseManager

logging.basicConfig(level=logging.INFO)

manager = DatabaseManager()

print("=== PhonePe Pulse Database Setup ===\n")

# Step 1
print("1. Testing connection...")
if manager.test_connection():
    print("   ✓ Connected\n")
else:
    print("   ✗ Connection failed!")
    exit(1)

# Step 2
print("2. Creating tables...")
if manager.setup_database():
    print("   ✓ Tables ready\n")
else:
    print("   ✗ Failed to create tables!")
    exit(1)

# Step 3
print("3. Syncing data...")
if manager.sync_data():
    print("   ✓ Data synced\n")

# Step 4
print("4. Database status...")
stats = manager.get_database_stats()
for table, count in stats.items():
    print(f"   • {table}: {count:,} rows")

print("\n✓ All done! Run: streamlit run app/main.py")


# Example 10: Closing Connection
# ==============================

from src.data_loader import DataLoader

loader = DataLoader()

# Use database
data = loader.load_from_database('transaction')

# Close connection when done
loader.close_db_connection()

print("Database connection closed")
