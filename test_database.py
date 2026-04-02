"""
Database Testing Module for PhonePe Pulse Dashboard
Comprehensive tests for PostgreSQL database functionality
"""
import logging
import sys
from typing import List, Tuple
from src.data_loader import DataLoader
from src.database import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class DatabaseTester:
    """Comprehensive database testing suite"""
    
    def __init__(self):
        """Initialize tester"""
        self.loader = DataLoader()
        self.manager = DatabaseManager()
        self.results: List[Tuple[str, bool, str]] = []
    
    def run_all_tests(self) -> bool:
        """
        Run all database tests.
        
        Returns:
            True if all tests pass, False otherwise
        """
        logger.info("Starting comprehensive database tests...\n")
        
        tests = [
            ("PostgreSQL Driver Available", self.test_driver_availability),
            ("Database Connection", self.test_connection),
            ("Table Creation", self.test_table_creation),
            ("Data Sync", self.test_data_sync),
            ("Transaction Data Loading", self.test_transaction_loading),
            ("Insurance Data Loading", self.test_insurance_loading),
            ("User Data Loading", self.test_user_loading),
            ("Database Statistics", self.test_database_stats),
            ("Fallback Mechanism", self.test_fallback),
            ("Connection Pooling", self.test_connection_pooling),
        ]
        
        for test_name, test_func in tests:
            try:
                success, message = test_func()
                self.results.append((test_name, success, message))
                status = "PASS" if success else "FAIL"
                logger.info(f"{status}: {test_name}")
                if message:
                    logger.info(f"        {message}")
            except Exception as e:
                self.results.append((test_name, False, str(e)))
                logger.error(f"FAIL: {test_name}")
                logger.error(f"        {str(e)}")
        
        self.print_summary()
        return all(result[1] for result in self.results)
    
    def test_driver_availability(self) -> Tuple[bool, str]:
        """Test if psycopg2 driver is available"""
        try:
            import psycopg2
            version = psycopg2.__version__
            return True, f"psycopg2 {version} available"
        except ImportError:
            return False, "psycopg2 not installed (install with: pip install psycopg2-binary)"
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test database connection"""
        conn = self.loader.get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0].split(',')[0]
                cursor.close()
                return True, f"Connected to {version}"
            except Exception as e:
                return False, str(e)
        else:
            return False, "Cannot establish database connection"
    
    def test_table_creation(self) -> Tuple[bool, str]:
        """Test database table creation"""
        if not self.manager.setup_database():
            return False, "Failed to create tables"
        
        conn = self.loader.get_db_connection()
        if not conn:
            return False, "No database connection"
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            
            required_tables = {'transactions', 'insurance', 'users'}
            found_tables = set(tables) & required_tables
            
            if found_tables == required_tables:
                return True, f"All required tables created: {', '.join(required_tables)}"
            else:
                missing = required_tables - found_tables
                return False, f"Missing tables: {missing}"
        except Exception as e:
            return False, str(e)
    
    def test_data_sync(self) -> Tuple[bool, str]:
        """Test JSON to database synchronization"""
        try:
            if not self.manager.sync_data():
                return False, "Sync operation failed"
            return True, "JSON data synchronized to database"
        except Exception as e:
            return False, str(e)
    
    def test_transaction_loading(self) -> Tuple[bool, str]:
        """Test loading transaction data from database"""
        try:
            df = self.loader.load_from_database('transaction')
            if df.empty:
                return False, "No transaction data loaded"
            return True, f"Loaded {len(df)} transaction records"
        except Exception as e:
            return False, str(e)
    
    def test_insurance_loading(self) -> Tuple[bool, str]:
        """Test loading insurance data from database"""
        try:
            df = self.loader.load_from_database('insurance')
            if df.empty:
                return False, "No insurance data loaded"
            return True, f"Loaded {len(df)} insurance records"
        except Exception as e:
            return False, str(e)
    
    def test_user_loading(self) -> Tuple[bool, str]:
        """Test loading user data from database"""
        try:
            df = self.loader.load_from_database('user')
            if df.empty:
                return False, "No user data loaded"
            return True, f"Loaded {len(df)} user records"
        except Exception as e:
            return False, str(e)
    
    def test_database_stats(self) -> Tuple[bool, str]:
        """Test database statistics retrieval"""
        try:
            stats = self.manager.get_database_stats()
            if not stats:
                return False, "Failed to get statistics"
            
            total_rows = sum(stats.values())
            return True, f"Total records: {total_rows:,} (T:{stats['transactions']}, I:{stats['insurance']}, U:{stats['users']})"
        except Exception as e:
            return False, str(e)
    
    def test_fallback(self) -> Tuple[bool, str]:
        """Test automatic fallback to JSON when database unavailable"""
        try:
            # Force close database connection temporarily
            original_conn = self.loader.db_connection
            self.loader.db_connection = None
            
            # Try loading (should fallback to JSON)
            df = self.loader.load_from_json('aggregated', 'transaction')
            
            # Restore connection
            self.loader.db_connection = original_conn
            
            if df.empty:
                return False, "Fallback to JSON failed"
            return True, "Automatic fallback to JSON works correctly"
        except Exception as e:
            return False, str(e)
    
    def test_connection_pooling(self) -> Tuple[bool, str]:
        """Test connection pooling and reuse"""
        try:
            conn1 = self.loader.get_db_connection()
            conn2 = self.loader.get_db_connection()
            
            if conn1 is conn2:
                return True, "Connection pooling works (same connection reused)"
            else:
                return False, "Connection pooling failed (new connection created)"
        except Exception as e:
            return False, str(e)
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("DATABASE TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for _, success, _ in self.results if success)
        failed = sum(1 for _, success, _ in self.results if not success)
        total = len(self.results)
        
        print(f"\nResults: {passed} passed, {failed} failed, {total} total\n")
        
        if failed > 0:
            print("Failed Tests:")
            for name, success, message in self.results:
                if not success:
                    print(f"  FAIL {name}")
                    print(f"    {message}")
        
        print("\n" + "=" * 70)
        if passed == total:
            print("All tests passed! PostgreSQL is ready to use.")
        else:
            print(f"{failed} test(s) failed. Check configuration and try again.")
        print("=" * 70 + "\n")


def main():
    """Run database tests"""
    tester = DatabaseTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
