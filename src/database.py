"""
Database Management Module for PhonePe Pulse Dashboard
Provides utilities for PostgreSQL database setup and management
"""
import logging
import sys
from typing import Optional
from src.data_loader import DataLoader

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manager class for database operations"""
    
    def __init__(self):
        """Initialize database manager"""
        self.loader = DataLoader()
    
    def test_connection(self) -> bool:
        """
        Test PostgreSQL database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        logger.info("Testing PostgreSQL connection...")
        try:
            conn = self.loader.get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                cursor.close()
                logger.info(f"✓ Connected successfully. PostgreSQL: {version[0].split(',')[0]}")
                return True
            else:
                logger.error("✗ Failed to connect to database")
                return False
        except Exception as e:
            logger.error(f"✗ Connection test failed: {str(e)}")
            return False
    
    def setup_database(self) -> bool:
        """
        Setup database tables.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Setting up PostgreSQL database tables...")
        try:
            if self.loader.create_tables():
                logger.info("✓ Database tables created/verified successfully")
                return True
            else:
                logger.error("✗ Failed to create database tables")
                return False
        except Exception as e:
            logger.error(f"✗ Database setup failed: {str(e)}")
            return False
    
    def sync_data(self) -> bool:
        """
        Synchronize data from JSON files to database.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Synchronizing data from JSON files to database...")
        try:
            if self.loader.sync_json_to_database():
                logger.info("✓ Data synchronized successfully")
                return True
            else:
                logger.error("✗ Failed to synchronize data")
                return False
        except Exception as e:
            logger.error(f"✗ Data sync failed: {str(e)}")
            return False
    
    def get_database_stats(self) -> Optional[dict]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with table statistics or None if error
        """
        conn = self.loader.get_db_connection()
        if not conn:
            logger.error("Cannot get stats: No database connection")
            return None
        
        try:
            cursor = conn.cursor()
            stats = {}
            
            tables = ['transactions', 'insurance', 'users']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            
            cursor.close()
            return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return None
    
    def clear_database(self, confirm: bool = False) -> bool:
        """
        Clear all data from database tables.
        
        Args:
            confirm: Require confirmation before clearing
            
        Returns:
            True if successful, False otherwise
        """
        if confirm:
            response = input("Are you sure you want to clear all database data? (yes/no): ")
            if response.lower() != 'yes':
                logger.info("Clear operation cancelled")
                return False
        
        conn = self.loader.get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions; DELETE FROM insurance; DELETE FROM users;")
            conn.commit()
            logger.info("✓ Database cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()


def main():
    """Command-line interface for database management"""
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(
        description='PhonePe Pulse Database Management Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/database.py --test          Test database connection
  python src/database.py --setup         Create database tables
  python src/database.py --sync          Sync JSON data to database
  python src/database.py --stats         Show database statistics
  python src/database.py --full-setup    Test, setup, and sync in one command
        """
    )
    
    parser.add_argument('--test', action='store_true', help='Test database connection')
    parser.add_argument('--setup', action='store_true', help='Create database tables')
    parser.add_argument('--sync', action='store_true', help='Sync JSON data to database')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--clear', action='store_true', help='Clear all database data (requires confirmation)')
    parser.add_argument('--full-setup', action='store_true', help='Complete setup: test, create, and sync')
    
    args = parser.parse_args()
    
    if not any([args.test, args.setup, args.sync, args.stats, args.clear, args.full_setup]):
        parser.print_help()
        return
    
    manager = DatabaseManager()
    
    try:
        if args.test:
            manager.test_connection()
        
        if args.setup or args.full_setup:
            manager.setup_database()
        
        if args.sync or args.full_setup:
            manager.sync_data()
        
        if args.stats:
            stats = manager.get_database_stats()
            if stats:
                print("\nDatabase Statistics:")
                print("-" * 40)
                for table, count in stats.items():
                    print(f"{table:20s}: {count:,} rows")
                print("-" * 40)
        
        if args.clear:
            manager.clear_database(confirm=True)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
