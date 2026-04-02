"""
Data Loading Module for PhonePe Pulse Dashboard
Handles loading data from database and JSON files
"""
import os
import json
import logging
from typing import Optional, Dict, Tuple
import pandas as pd
from pathlib import Path
from config.settings import config
from src.utils import clean_state_names

try:
    import psycopg2
    from psycopg2.extras import execute_values
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    psycopg2 = None
    execute_values = None

logger = logging.getLogger(__name__)


class DataLoader:
    """Main class for loading PhonePe Pulse data"""
    
    def __init__(self):
        """Initialize data loader with configuration"""
        self.config = config
        self.geojson_data: Optional[Dict] = None
        self._cache: Dict = {}
        self.db_connection = None
    
    def get_db_connection(self):
        """
        Get PostgreSQL database connection.
        
        Returns:
            Database connection object or None if DB not available
        """
        if not DB_AVAILABLE:
            logger.warning("psycopg2 not installed. Database functionality unavailable.")
            return None
        
        if self.db_connection is not None:
            try:
                # Test connection
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return self.db_connection
            except Exception as e:
                logger.warning(f"Database connection lost, reconnecting: {str(e)}")
                self.db_connection = None
        
        try:
            conn_params = self.config.db.get_connection_kwargs()
            self.db_connection = psycopg2.connect(**conn_params)
            logger.info("Successfully connected to PostgreSQL database")
            return self.db_connection
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
            return None
    
    def close_db_connection(self):
        """Close database connection"""
        if self.db_connection:
            try:
                self.db_connection.close()
                self.db_connection = None
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {str(e)}")
    
    def create_tables(self) -> bool:
        """
        Create database tables for PhonePe Pulse data.
        
        Returns:
            True if successful, False otherwise
        """
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Create transaction table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    state VARCHAR(100),
                    year INTEGER,
                    quarter INTEGER,
                    transaction_type VARCHAR(100),
                    transaction_count BIGINT,
                    transaction_amount BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(state, year, quarter, transaction_type)
                );
                
                CREATE INDEX IF NOT EXISTS idx_transactions_state_year ON transactions(state, year);
                CREATE INDEX IF NOT EXISTS idx_transactions_year_quarter ON transactions(year, quarter);
            """)
            
            # Create insurance table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS insurance (
                    id SERIAL PRIMARY KEY,
                    state VARCHAR(100),
                    year INTEGER,
                    quarter INTEGER,
                    insurance_type VARCHAR(100),
                    insurance_count BIGINT,
                    insurance_amount BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(state, year, quarter, insurance_type)
                );
                
                CREATE INDEX IF NOT EXISTS idx_insurance_state_year ON insurance(state, year);
                CREATE INDEX IF NOT EXISTS idx_insurance_year_quarter ON insurance(year, quarter);
            """)
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    state VARCHAR(100),
                    year INTEGER,
                    quarter INTEGER,
                    brands VARCHAR(100),
                    user_count BIGINT,
                    percentage REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(state, year, quarter, brands)
                );
                
                CREATE INDEX IF NOT EXISTS idx_users_state_year ON users(state, year);
                CREATE INDEX IF NOT EXISTS idx_users_year_quarter ON users(year, quarter);
            """)
            
            conn.commit()
            logger.info("Database tables created/verified successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
    
    def sync_json_to_database(self) -> bool:
        """
        Synchronize data from JSON files to PostgreSQL database.
        
        Returns:
            True if successful, False otherwise
        """
        conn = None
        try:
            # Get connection
            conn = self.get_db_connection()
            if not conn:
                logger.error("Cannot sync to database: No database connection")
                return False
            
            # Load all data from JSON FIRST
            logger.info("Loading data from JSON files for database sync...")
            
            transaction_df = self.load_from_json('aggregated', 'transaction')
            insurance_df = self.load_from_json('aggregated', 'insurance')
            user_df = self.load_from_json('aggregated', 'user')
            
            # Remove duplicates from dataframes
            logger.info(f"Deduplicating data...")
            if not transaction_df.empty:
                cols_to_check = ['States', 'Years', 'Quarter', 'Transaction_type']
                transaction_df = transaction_df.drop_duplicates(subset=cols_to_check, keep='first')
                logger.info(f"  Transactions after dedup: {len(transaction_df)} rows")
            
            if not insurance_df.empty:
                cols_to_check = ['States', 'Years', 'Quarter', 'Insurance_type']
                insurance_df = insurance_df.drop_duplicates(subset=cols_to_check, keep='first')
                logger.info(f"  Insurance after dedup: {len(insurance_df)} rows")
            
            if not user_df.empty:
                cols_to_check = ['States', 'Years', 'Quarter', 'Brands']
                user_df = user_df.drop_duplicates(subset=cols_to_check, keep='first')
                logger.info(f"  Users after dedup: {len(user_df)} rows")
            
            cursor = conn.cursor()
            
            # Drop and recreate tables for clean state
            try:
                cursor.execute("DROP TABLE IF EXISTS transactions CASCADE;")
                cursor.execute("DROP TABLE IF EXISTS insurance CASCADE;")
                cursor.execute("DROP TABLE IF EXISTS users CASCADE;")
                conn.commit()
                logger.info("Dropped existing tables")
            except Exception as e:
                logger.warning(f"DROP warning: {str(e)}")
                conn.rollback()
            
            # Recreate tables
            self.create_tables()
            
            # Get fresh cursor after table recreation
            cursor = conn.cursor()
            
            # Insert transaction data
            if not transaction_df.empty:
                self._insert_data_to_db(cursor, transaction_df, 'transactions', 'transaction')
            
            # Insert insurance data 
            if not insurance_df.empty:
                self._insert_data_to_db(cursor, insurance_df, 'insurance', 'insurance')
            
            # Insert user data
            if not user_df.empty:
                self._insert_data_to_db(cursor, user_df, 'users', 'user')
            
            conn.commit()
            logger.info("Successfully synchronized JSON data to PostgreSQL database")
            return True
        
        except Exception as e:
            logger.error(f"Error syncing data to database: {str(e)}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return False
        finally:
            if conn:
                try:
                    conn.close()
                    self.db_connection = None  # Reset connection pool
                except:
                    pass
    
    def _insert_data_to_db(self, cursor, df: pd.DataFrame, table_name: str, data_type: str):
        """
        Insert data into database table.
        
        Args:
            cursor: Database cursor
            df: DataFrame with data to insert
            table_name: Target table name
            data_type: Type of data ('transaction', 'insurance', 'user')
        """
        try:
            if data_type == 'transaction':
                columns = ['state', 'year', 'quarter', 'transaction_type', 'transaction_count', 'transaction_amount']
                column_names = 'state, year, quarter, transaction_type, transaction_count, transaction_amount'
                # Rename columns to match database schema
                df = df.rename(columns={
                    'States': 'state',
                    'Years': 'year',
                    'Quarter': 'quarter',
                    'Transaction_type': 'transaction_type',
                    'Transaction_count': 'transaction_count',
                    'Transaction_amount': 'transaction_amount'
                })
            
            elif data_type == 'insurance':
                columns = ['state', 'year', 'quarter', 'insurance_type', 'insurance_count', 'insurance_amount']
                column_names = 'state, year, quarter, insurance_type, insurance_count, insurance_amount'
                df = df.rename(columns={
                    'States': 'state',
                    'Years': 'year',
                    'Quarter': 'quarter',
                    'Insurance_type': 'insurance_type',
                    'Insurance_count': 'insurance_count',
                    'Insurance_amount': 'insurance_amount'
                })
            
            elif data_type == 'user':
                columns = ['state', 'year', 'quarter', 'brands', 'user_count', 'percentage']
                column_names = 'state, year, quarter, brands, user_count, percentage'
                df = df.rename(columns={
                    'States': 'state',
                    'Years': 'year',
                    'Quarter': 'quarter',
                    'Brands': 'brands',
                    'User_count': 'user_count',
                    'Percentage': 'percentage'
                })
            
            # Delete existing data for this batch to avoid duplicates
            df_distinct = df[['state', 'year', 'quarter']].drop_duplicates()
            for _, row in df_distinct.iterrows():
                cursor.execute(
                    f"DELETE FROM {table_name} WHERE state = %s AND year = %s AND quarter = %s",
                    (row['state'], row['year'], row['quarter'])
                )
            
            # Insert new data
            tuples = [tuple(row[col] for col in columns) for _, row in df[columns].iterrows()]
            
            # Build INSERT query for execute_values (which uses %s, not (%s, %s, ...))
            insert_query = f"INSERT INTO {table_name} ({column_names}) VALUES %s"
            
            execute_values(cursor, insert_query, tuples, page_size=1000)
            logger.info(f"Inserted {len(tuples)} rows into {table_name}")
        
        except Exception as e:
            logger.error(f"Error inserting data into {table_name}: {str(e)}")
            raise
    
    def load_from_database(self, category: str) -> pd.DataFrame:
        """
        Load data from PostgreSQL database.
        
        Args:
            category: Data category ('transaction', 'insurance', 'user')
            
        Returns:
            DataFrame with data from database
        """
        cache_key = f"db_{category}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        conn = self.get_db_connection()
        if not conn:
            logger.warning("Database not available, falling back to JSON")
            return self.load_from_json('aggregated', category)
        
        try:
            if category == 'transaction':
                query = """
                    SELECT state AS "States", year AS "Years", quarter AS "Quarter",
                           transaction_type AS "Transaction_type",
                           transaction_count AS "Transaction_count",
                           transaction_amount AS "Transaction_amount"
                    FROM transactions
                    ORDER BY year, quarter, state
                """
            elif category == 'insurance':
                query = """
                    SELECT state AS "States", year AS "Years", quarter AS "Quarter",
                           insurance_type AS "Insurance_type",
                           insurance_count AS "Insurance_count",
                           insurance_amount AS "Insurance_amount"
                    FROM insurance
                    ORDER BY year, quarter, state
                """
            elif category == 'user':
                query = """
                    SELECT state AS "States", year AS "Years", quarter AS "Quarter",
                           brands AS "Brands",
                           user_count AS "User_count",
                           percentage AS "Percentage"
                    FROM users
                    ORDER BY year, quarter, state
                """
            else:
                logger.error(f"Unknown category: {category}")
                return pd.DataFrame()
            
            df = pd.read_sql_query(query, conn)
            self._cache[cache_key] = df
            logger.info(f"Loaded {len(df)} rows for {category} data from database")
            return df
        
        except Exception as e:
            logger.error(f"Error loading {category} data from database: {str(e)}")
            logger.info("Falling back to JSON data loading")
            return self.load_from_json('aggregated', category)
    
    
    def load_from_json(self, data_type: str, category: str) -> pd.DataFrame:
        """
        Load data from JSON files (both country and state level).
        
        Args:
            data_type: Type of data ('aggregated', 'map', 'top')
            category: Category of data ('insurance', 'transaction', 'user')
            
        Returns:
            Loaded dataframe
        """
        cache_key = f"{data_type}_{category}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        logger.info(f"Loading {data_type} {category} data from all sources")
        
        # Load both country-level and state-level data
        dfs = []
        
        # Get country-level path
        country_path = self._get_country_data_path(data_type, category)
        if country_path and os.path.exists(country_path):
            df_country = self._extract_from_path(country_path, category)
            if not df_country.empty:
                dfs.append(df_country)
                logger.info(f"  Loaded country-level data: {len(df_country)} rows")
        
        # Get state-level path
        state_path = self._get_data_path(data_type, category)
        if state_path and os.path.exists(state_path):
            df_state = self._extract_from_path(state_path, category)
            if not df_state.empty:
                dfs.append(df_state)
                logger.info(f"  Loaded state-level data: {len(df_state)} rows")
        
        # Combine all dataframes
        if dfs:
            df = pd.concat(dfs, ignore_index=True)
        else:
            logger.warning(f"No data found for {data_type} {category}")
            df = pd.DataFrame()
        
        self._cache[cache_key] = df
        return df
    
    def _get_data_path(self, data_type: str, category: str) -> str:
        """Get the appropriate data path (state-level)"""
        paths = {
            ('aggregated', 'insurance'): self.config.AGG_INSURANCE_PATH,
            ('aggregated', 'transaction'): self.config.AGG_TRANSACTION_PATH,
            ('aggregated', 'user'): self.config.AGG_USER_PATH,
            ('map', 'insurance'): self.config.MAP_INSURANCE_PATH,
            ('map', 'transaction'): self.config.MAP_TRANSACTION_PATH,
            ('map', 'user'): self.config.MAP_USER_PATH,
            ('top', 'insurance'): self.config.TOP_INSURANCE_PATH,
            ('top', 'transaction'): self.config.TOP_TRANSACTION_PATH,
            ('top', 'user'): self.config.TOP_USER_PATH,
        }
        return paths.get((data_type, category), "")
    
    def _get_country_data_path(self, data_type: str, category: str) -> str:
        """Get the appropriate data path (country-level only for aggregated)"""
        if data_type != 'aggregated':
            return None
        
        paths = {
            ('aggregated', 'insurance'): self.config.AGG_INSURANCE_COUNTRY_PATH,
            ('aggregated', 'transaction'): self.config.AGG_TRANSACTION_COUNTRY_PATH,
            ('aggregated', 'user'): self.config.AGG_USER_COUNTRY_PATH,
        }
        return paths.get((data_type, category), None)
    
    def _extract_from_path(self, path: str, category: str) -> pd.DataFrame:
        """
        Extract and process data from directory path.
        
        Args:
            path: Path to data directory
            category: Data category
            
        Returns:
            Processed dataframe
        """
        if category == 'insurance':
            return self._extract_insurance_data(path)
        elif category == 'transaction':
            return self._extract_transaction_data(path)
        elif category == 'user':
            return self._extract_user_data(path)
        else:
            logger.error(f"Unknown category: {category}")
            return pd.DataFrame()
    
    def _extract_insurance_data(self, path: str) -> pd.DataFrame:
        """Extract insurance data from path - handles PhonePe Pulse JSON structure"""
        columns = {
            "States": [], "Years": [], "Quarter": [],
            "Insurance_type": [], "Insurance_count": [], "Insurance_amount": []
        }
        
        try:
            # Handle both state-level and country-level paths
            for root, dirs, files in os.walk(path):
                for file in files:
                    if not file.endswith(".json"):
                        continue
                    
                    try:
                        file_path = os.path.join(root, file)
                        # Normalize path separators for consistent processing
                        file_path_normalized = file_path.replace('\\', '/')
                        
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        
                        if not data.get("success", False) or "data" not in data:
                            continue
                        
                        # Extract quarter from filename
                        quarter = int(file.split('.')[0])
                        
                        # Extract year from path
                        year = None
                        path_parts = file_path_normalized.split('/')
                        for i, part in enumerate(path_parts):
                            if part.isdigit() and len(part) == 4:
                                year = int(part)
                                break
                        
                        if year is None:
                            continue
                        
                        # Extract state name from path
                        # State is the part immediately after 'state' folder, or 'India' if country-level
                        state = "India"
                        if "state" in file_path_normalized.lower():
                            try:
                                state_idx = path_parts.index('state')
                                if state_idx + 1 < len(path_parts):
                                    state = path_parts[state_idx + 1]
                            except (ValueError, IndexError):
                                pass
                        
                        # Parse transactionData structure for insurance
                        tx_data = data.get("data", {}).get("transactionData", [])
                        
                        for trans in tx_data:
                            trans_type = trans.get("name", "Insurance")
                            for payment_inst in trans.get("paymentInstruments", []):
                                if payment_inst.get("type") == "TOTAL":
                                    columns["States"].append(state)
                                    columns["Years"].append(year)
                                    columns["Quarter"].append(quarter)
                                    columns["Insurance_type"].append(trans_type)
                                    columns["Insurance_count"].append(payment_inst.get("count", 0))
                                    columns["Insurance_amount"].append(payment_inst.get("amount", 0))
                    
                    except Exception as e:
                        logger.debug(f"Error processing file {file}: {str(e)}")
                        continue
        
        except Exception as e:
            logger.error(f"Error extracting insurance data from {path}: {str(e)}")
        
        df = pd.DataFrame(columns)
        return clean_state_names(df) if not df.empty else df
    
    def _extract_transaction_data(self, path: str) -> pd.DataFrame:
        """Extract transaction data from path - handles PhonePe Pulse JSON structure"""
        columns = {
            "States": [], "Years": [], "Quarter": [],
            "Transaction_type": [], "Transaction_count": [], "Transaction_amount": []
        }
        
        try:
            # Handle both state-level and country-level paths
            for root, dirs, files in os.walk(path):
                for file in files:
                    if not file.endswith(".json"):
                        continue
                    
                    try:
                        file_path = os.path.join(root, file)
                        # Normalize path separators for consistent processing
                        file_path_normalized = file_path.replace('\\', '/')
                        
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        
                        if not data.get("success", False) or "data" not in data:
                            continue
                        
                        # Extract quarter from filename
                        quarter = int(file.split('.')[0])
                        
                        # Extract year from path
                        year = None
                        path_parts = file_path_normalized.split('/')
                        for i, part in enumerate(path_parts):
                            if part.isdigit() and len(part) == 4:
                                year = int(part)
                                break
                        
                        if year is None:
                            continue
                        
                        # Extract state name from path
                        # State is the part immediately after 'state' folder, or 'India' if country-level
                        state = "India"
                        if "state" in file_path_normalized.lower():
                            try:
                                state_idx = path_parts.index('state')
                                if state_idx + 1 < len(path_parts):
                                    state = path_parts[state_idx + 1]
                            except (ValueError, IndexError):
                                pass
                        
                        # Parse transactionData structure
                        tx_data = data.get("data", {}).get("transactionData", [])
                        
                        for trans in tx_data:
                            trans_type = trans.get("name", "Unknown")
                            for payment_inst in trans.get("paymentInstruments", []):
                                if payment_inst.get("type") == "TOTAL":
                                    columns["States"].append(state)
                                    columns["Years"].append(year)
                                    columns["Quarter"].append(quarter)
                                    columns["Transaction_type"].append(trans_type)
                                    columns["Transaction_count"].append(payment_inst.get("count", 0))
                                    columns["Transaction_amount"].append(payment_inst.get("amount", 0))
                    
                    except Exception as e:
                        logger.debug(f"Error processing file {file}: {str(e)}")
                        continue
        
        except Exception as e:
            logger.error(f"Error extracting transaction data from {path}: {str(e)}")
        
        df = pd.DataFrame(columns)
        return clean_state_names(df) if not df.empty else df
    
    def _extract_user_data(self, path: str) -> pd.DataFrame:
        """Extract user data from path - handles PhonePe Pulse JSON structure"""
        columns = {
            "States": [], "Years": [], "Quarter": [],
            "Brands": [], "User_count": [], "Percentage": []
        }
        
        try:
            # Handle both state-level and country-level paths
            for root, dirs, files in os.walk(path):
                for file in files:
                    if not file.endswith(".json"):
                        continue
                    
                    try:
                        file_path = os.path.join(root, file)
                        # Normalize path separators for consistent processing
                        file_path_normalized = file_path.replace('\\', '/')
                        
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        
                        if not data.get("success", False) or "data" not in data:
                            continue
                        
                        # Extract quarter from filename
                        quarter = int(file.split('.')[0])
                        
                        # Extract year from path
                        year = None
                        path_parts = file_path_normalized.split('/')
                        for i, part in enumerate(path_parts):
                            if part.isdigit() and len(part) == 4:
                                year = int(part)
                                break
                        
                        if year is None:
                            continue
                        
                        # Extract state name from path
                        # State is the part immediately after 'state' folder, or 'India' if country-level
                        state = "India"
                        if "state" in file_path_normalized.lower():
                            try:
                                state_idx = path_parts.index('state')
                                if state_idx + 1 < len(path_parts):
                                    state = path_parts[state_idx + 1]
                            except (ValueError, IndexError):
                                pass
                        
                        # Parse usersByDevice structure
                        users_by_device = data.get("data", {}).get("usersByDevice", None)
                        
                        # Skip if usersByDevice is None or empty
                        if not users_by_device or not isinstance(users_by_device, list):
                            continue
                        
                        for device in users_by_device:
                            columns["States"].append(state)
                            columns["Years"].append(year)
                            columns["Quarter"].append(quarter)
                            columns["Brands"].append(device.get("brand", "Unknown"))
                            columns["User_count"].append(device.get("count", 0))
                            columns["Percentage"].append(device.get("percentage", 0))
                    
                    except Exception as e:
                        logger.debug(f"Error processing file {file}: {str(e)}")
                        continue
        
        except Exception as e:
            logger.error(f"Error extracting user data from {path}: {str(e)}")
        
        df = pd.DataFrame(columns)
        return clean_state_names(df) if not df.empty else df
    
    def get_geojson(self) -> Optional[Dict]:
        """
        Get GeoJSON data for map visualization.
        
        Returns:
            GeoJSON data or None
        """
        if self.geojson_data is not None:
            return self.geojson_data
        
        try:
            from src.utils import fetch_geojson
            self.geojson_data = fetch_geojson(self.config.GEOJSON_URL)
            return self.geojson_data
        except Exception as e:
            logger.error(f"Error loading GeoJSON: {str(e)}")
            return None


# Helper functions for backward compatibility
def load_aggregated_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all aggregated data"""
    loader = DataLoader()
    insurance = loader.load_from_json('aggregated', 'insurance')
    transaction = loader.load_from_json('aggregated', 'transaction')
    user = loader.load_from_json('aggregated', 'user')
    return insurance, transaction, user


def load_map_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all map data"""
    loader = DataLoader()
    insurance = loader.load_from_json('map', 'insurance')
    transaction = loader.load_from_json('map', 'transaction')
    user = loader.load_from_json('map', 'user')
    return insurance, transaction, user


def load_top_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all top data"""
    loader = DataLoader()
    insurance = loader.load_from_json('top', 'insurance')
    transaction = loader.load_from_json('top', 'transaction')
    user = loader.load_from_json('top', 'user')
    return insurance, transaction, user
