"""
Utility functions for PhonePe Pulse Dashboard
Common utility functions for data processing and validation
"""
import logging
from typing import Optional, Dict, List, Any
import pandas as pd
import json
import requests
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

GEOJSON_CACHE_PATH = Path(__file__).resolve().parent.parent / ".cache" / "india_states.geojson"


def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def clean_state_names(df: pd.DataFrame, state_column: str = "States") -> pd.DataFrame:
    """
    Clean and standardize state names in dataframe.
    
    Args:
        df: Input dataframe with state names
        state_column: Name of the state column
        
    Returns:
        Dataframe with cleaned state names
    """
    if df.empty or state_column not in df.columns:
        return df
    
    try:
        df = df.copy()
        df[state_column] = df[state_column].str.replace("andaman-&-nicobar-islands", "Andaman & Nicobar")
        df[state_column] = df[state_column].str.replace("-", " ")
        df[state_column] = df[state_column].str.title()
        df[state_column] = df[state_column].str.replace(
            "Dadra & Nagar Haveli & Daman & Diu",
            "Dadra And Nagar Haveli And Daman And Diu"
        )
        logger.debug(f"Cleaned state names in column '{state_column}'")
    except Exception as e:
        logger.error(f"Error cleaning state names: {str(e)}")
    
    return df


@lru_cache(maxsize=1)
def fetch_geojson(url: str) -> Optional[Dict[str, Any]]:
    """
    Fetch GeoJSON data with caching.
    
    Args:
        url: URL to fetch GeoJSON from
        
    Returns:
        Parsed GeoJSON data or None if fetch fails
    """
    if GEOJSON_CACHE_PATH.exists():
        try:
            with GEOJSON_CACHE_PATH.open("r", encoding="utf-8") as cache_file:
                data = json.load(cache_file)
            logger.info("GeoJSON data loaded from local cache")
            return data
        except (OSError, json.JSONDecodeError) as e:
            logger.warning(f"Error reading cached GeoJSON: {str(e)}")

    try:
        session = requests.Session()
        session.trust_env = False
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = json.loads(response.content)
        GEOJSON_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with GEOJSON_CACHE_PATH.open("w", encoding="utf-8") as cache_file:
            json.dump(data, cache_file)
        logger.info("GeoJSON data fetched successfully")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching GeoJSON: {str(e)}")
        if GEOJSON_CACHE_PATH.exists():
            try:
                with GEOJSON_CACHE_PATH.open("r", encoding="utf-8") as cache_file:
                    data = json.load(cache_file)
                logger.info("GeoJSON data loaded from local cache after fetch failure")
                return data
            except (OSError, json.JSONDecodeError) as cache_error:
                logger.error(f"Error reading cached GeoJSON after fetch failure: {str(cache_error)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing GeoJSON: {str(e)}")
        return None


def validate_dataframe(df: pd.DataFrame, required_columns: Optional[List[str]] = None) -> bool:
    """
    Validate dataframe and required columns.
    
    Args:
        df: Dataframe to validate
        required_columns: List of required column names
        
    Returns:
        True if valid, False otherwise
    """
    if df is None or df.empty:
        return False
    
    if required_columns:
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logger.warning(f"Missing required columns: {missing_cols}")
            return False
    
    return True


def get_available_years(df: pd.DataFrame) -> List[int]:
    """
    Get sorted list of available years from dataframe.
    
    Args:
        df: Dataframe containing 'Years' column
        
    Returns:
        Sorted list of years
    """
    if not validate_dataframe(df, required_columns=["Years"]):
        return []
    
    try:
        years = sorted(df["Years"].unique().astype(int))
        return years
    except Exception as e:
        logger.error(f"Error getting years: {str(e)}")
        return []


def get_available_quarters(df: pd.DataFrame) -> List[int]:
    """
    Get sorted list of available quarters from dataframe.
    
    Args:
        df: Dataframe containing 'Quarter' column
        
    Returns:
        Sorted list of quarters
    """
    if not validate_dataframe(df, required_columns=["Quarter"]):
        return []
    
    try:
        quarters = sorted(df["Quarter"].unique().astype(int))
        return quarters
    except Exception as e:
        logger.error(f"Error getting quarters: {str(e)}")
        return []


def get_available_states(df: pd.DataFrame) -> List[str]:
    """
    Get sorted list of available states from dataframe.
    
    Args:
        df: Dataframe containing 'States' column
        
    Returns:
        Sorted list of states
    """
    if not validate_dataframe(df, required_columns=["States"]):
        return []
    
    try:
        states = sorted(df["States"].unique())
        return states
    except Exception as e:
        logger.error(f"Error getting states: {str(e)}")
        return []


def format_currency(value: float, currency: str = "₹") -> str:
    """
    Format value as currency string.
    
    Args:
        value: Numeric value to format
        currency: Currency symbol
        
    Returns:
        Formatted currency string
    """
    try:
        if value >= 1_000_000_000:
            return f"{currency} {value/1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"{currency} {value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{currency} {value/1_000:.2f}K"
        else:
            return f"{currency} {value:.2f}"
    except Exception as e:
        logger.error(f"Error formatting currency: {str(e)}")
        return f"{currency} {value:.2f}"


def get_summary_stats(df: pd.DataFrame, amount_col: str = "Transaction_amount", 
                      count_col: str = "Transaction_count") -> Dict[str, Any]:
    """
    Calculate summary statistics from dataframe.
    
    Args:
        df: Input dataframe
        amount_col: Name of amount column
        count_col: Name of count column
        
    Returns:
        Dictionary with summary statistics
    """
    stats = {
        "total_amount": 0,
        "total_count": 0,
        "average_amount": 0,
        "max_amount": 0,
        "min_amount": 0
    }
    
    if df.empty:
        return stats
    
    try:
        if amount_col in df.columns:
            stats["total_amount"] = float(df[amount_col].sum())
            stats["max_amount"] = float(df[amount_col].max())
            stats["min_amount"] = float(df[amount_col].min())
            stats["average_amount"] = float(df[amount_col].mean())
        
        if count_col in df.columns:
            stats["total_count"] = int(df[count_col].sum())
    except Exception as e:
        logger.error(f"Error calculating summary stats: {str(e)}")
    
    return stats
