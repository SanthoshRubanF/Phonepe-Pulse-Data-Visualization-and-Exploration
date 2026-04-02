"""
Example script demonstrating PostgreSQL database functionality
Run this to test and configure PostgreSQL for PhonePe Pulse dashboard
"""
import logging
from src.database import DatabaseManager
from src.data_loader import DataLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def print_section(title):
    """Print formatted section title"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def main():
    """Main example function"""
    
    print_section("PhonePe Pulse - PostgreSQL Database Setup Example")
    
    # Initialize database manager
    manager = DatabaseManager()
    
    # Step 1: Test connection
    print_section("Step 1: Testing Database Connection")
    print("Attempting to connect to PostgreSQL...")
    if not manager.test_connection():
        print("\n⚠️  Database connection failed!")
        print("Please ensure:")
        print("  1. PostgreSQL is installed and running")
        print("  2. Database credentials are correct in .env file")
        print("  3. Database 'phonepe' exists")
        return
    
    # Step 2: Setup database
    print_section("Step 2: Setting Up Database Tables")
    print("Creating necessary tables and indexes...")
    if not manager.setup_database():
        print("\n⚠️  Failed to create database tables")
        return
    
    # Step 3: Show current stats
    print_section("Step 3: Current Database Status")
    stats = manager.get_database_stats()
    if stats:
        print("Current row counts:")
        for table, count in stats.items():
            print(f"  • {table:20s}: {count:,} rows")
    
    # Step 4: Sync data
    print_section("Step 4: Sync JSON Data to Database")
    user_input = input("Do you want to sync data from JSON files to database? (yes/no): ").lower()
    if user_input == 'yes':
        print("Synchronizing data...")
        if manager.sync_data():
            print("\n✓ Sync completed successfully!")
            
            # Show updated stats
            print_section("Updated Database Status")
            stats = manager.get_database_stats()
            if stats:
                print("New row counts:")
                for table, count in stats.items():
                    print(f"  • {table:20s}: {count:,} rows")
        else:
            print("\n⚠️  Data sync failed")
    else:
        print("Skipped data sync")
    
    # Step 5: Test loading from database
    print_section("Step 5: Testing Data Loading from Database")
    print("Attempting to load data from database...")
    
    loader = DataLoader()
    try:
        # Load transaction data
        print("\nLoading transaction data...")
        transactions = loader.load_from_database('transaction')
        print(f"✓ Loaded {len(transactions)} transaction records")
        print(f"  Columns: {list(transactions.columns)}")
        if not transactions.empty:
            print(f"  Sample data:")
            print(transactions.head(2).to_string(index=False))
        
        # Load insurance data
        print("\nLoading insurance data...")
        insurance = loader.load_from_database('insurance')
        print(f"✓ Loaded {len(insurance)} insurance records")
        
        # Load user data
        print("\nLoading user data...")
        users = loader.load_from_database('user')
        print(f"✓ Loaded {len(users)} user records")
        
    except Exception as e:
        print(f"✗ Error loading data: {str(e)}")
        return
    
    # Final summary
    print_section("Setup Complete!")
    print("✓ PostgreSQL database is configured and ready to use!")
    print("\nNext steps:")
    print("  1. Run the dashboard: streamlit run app/main.py")
    print("  2. The dashboard will automatically use PostgreSQL for data")
    print("  3. Database features:")
    print("     • Faster data loading for large datasets")
    print("     • Optimized queries with indexes")
    print("     • Automatic fallback to JSON if DB unavailable")
    print("\nFor more info, see DATABASE_SETUP.md")
    print("To manage database, use: python src/database.py --help\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
