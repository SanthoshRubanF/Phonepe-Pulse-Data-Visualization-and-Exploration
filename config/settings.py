"""
Configuration and Settings Module for PhonePe Pulse Dashboard
Centralized settings for database, paths, and application configuration
"""
import os
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables loading
def load_env_vars():
    """Load environment variables with defaults"""
    from dotenv import load_dotenv
    env_path = BASE_DIR / '.env'
    if env_path.exists():
        load_dotenv(env_path)


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = None
    user: str = None
    password: str = None
    database: str = None
    port: str = None
    
    def __post_init__(self):
        """Load environment variables after initialization"""
        self.host = os.getenv("DB_HOST", "127.0.0.1")  # Changed default from localhost to 127.0.0.1
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "password")
        self.database = os.getenv("DB_NAME", "phonepe")
        self.port = os.getenv("DB_PORT", "5432")
    
    def get_connection_kwargs(self) -> Dict:
        """Return connection parameters as dictionary"""
        return {
            "host": self.host,
            "user": self.user,
            "password": self.password,
            "database": self.database,
            "port": self.port
        }


@dataclass
class DataPaths:
    """Data path configuration"""
    
    def __post_init__(self):
        """Initialize data paths"""
        base_data_path = self._get_data_base_path()
        self.base_data_path = base_data_path
        
        # Aggregated data paths - COUNTRY level (2018-2024)
        self.agg_insurance_country = os.path.join(base_data_path, "aggregated/insurance/country/india/")
        self.agg_transaction_country = os.path.join(base_data_path, "aggregated/transaction/country/india/")
        self.agg_user_country = os.path.join(base_data_path, "aggregated/user/country/india/")
        
        # Aggregated data paths - STATE level
        self.agg_insurance = os.path.join(base_data_path, "aggregated/insurance/country/india/state/")
        self.agg_transaction = os.path.join(base_data_path, "aggregated/transaction/country/india/state/")
        self.agg_user = os.path.join(base_data_path, "aggregated/user/country/india/state/")
        
        # Map data paths
        self.map_insurance = os.path.join(base_data_path, "map/insurance/hover/country/india/state/")
        self.map_transaction = os.path.join(base_data_path, "map/transaction/hover/country/india/state/")
        self.map_user = os.path.join(base_data_path, "map/user/hover/country/india/state/")
        
        # Top data paths
        self.top_insurance = os.path.join(base_data_path, "top/insurance/country/india/state/")
        self.top_transaction = os.path.join(base_data_path, "top/transaction/country/india/state/")
        self.top_user = os.path.join(base_data_path, "top/user/country/india/state/")
    
    @staticmethod
    def _get_data_base_path() -> str:
        """Get data base path from environment or default locations"""
        env_path = os.getenv("DATA_BASE_PATH")
        if env_path:
            candidate = Path(env_path).expanduser()
            if not candidate.is_absolute():
                candidate = BASE_DIR / candidate
            if candidate.exists():
                return str(candidate.resolve())

        default_path = BASE_DIR / "pulse" / "data"
        return str(default_path.resolve())


@dataclass
class AppConfig:
    """Application configuration"""
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    theme: str = os.getenv("THEME", "light")
    
    # URL for GeoJSON data
    geojson_url: str = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"


class Config:
    """Main configuration class"""
    
    def __init__(self):
        load_env_vars()
        self.db = DatabaseConfig()
        self.paths = DataPaths()
        self.app = AppConfig()
    
    # Commonly used attributes for backward compatibility
    @property
    def DB_HOST(self) -> str:
        return self.db.host
    
    @property
    def DB_USER(self) -> str:
        return self.db.user
    
    @property
    def DB_PASSWORD(self) -> str:
        return self.db.password
    
    @property
    def DB_NAME(self) -> str:
        return self.db.database
    
    @property
    def DB_PORT(self) -> str:
        return self.db.port
    
    @property
    def DATA_BASE_PATH(self) -> str:
        return self.paths.base_data_path
    
    @property
    def AGG_INSURANCE_PATH(self) -> str:
        return self.paths.agg_insurance
    
    @property
    def AGG_INSURANCE_COUNTRY_PATH(self) -> str:
        return self.paths.agg_insurance_country
    
    @property
    def AGG_TRANSACTION_PATH(self) -> str:
        return self.paths.agg_transaction
    
    @property
    def AGG_TRANSACTION_COUNTRY_PATH(self) -> str:
        return self.paths.agg_transaction_country
    
    @property
    def AGG_USER_PATH(self) -> str:
        return self.paths.agg_user
    
    @property
    def AGG_USER_COUNTRY_PATH(self) -> str:
        return self.paths.agg_user_country
    
    @property
    def MAP_INSURANCE_PATH(self) -> str:
        return self.paths.map_insurance
    
    @property
    def MAP_TRANSACTION_PATH(self) -> str:
        return self.paths.map_transaction
    
    @property
    def MAP_USER_PATH(self) -> str:
        return self.paths.map_user
    
    @property
    def TOP_INSURANCE_PATH(self) -> str:
        return self.paths.top_insurance
    
    @property
    def TOP_TRANSACTION_PATH(self) -> str:
        return self.paths.top_transaction
    
    @property
    def TOP_USER_PATH(self) -> str:
        return self.paths.top_user
    
    @property
    def GEOJSON_URL(self) -> str:
        return self.app.geojson_url


# Global configuration instance
config = Config()
