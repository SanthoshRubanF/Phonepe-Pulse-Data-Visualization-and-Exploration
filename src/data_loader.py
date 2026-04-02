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

logger = logging.getLogger(__name__)


class DataLoader:
    """Main class for loading PhonePe Pulse data"""
    
    def __init__(self):
        """Initialize data loader with configuration"""
        self.config = config
        self.geojson_data: Optional[Dict] = None
        self._cache: Dict = {}
    
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
