"""
Helper utilities for data processing and transformations.
"""

from datetime import datetime, date, timedelta
import pandas as pd
import re
from typing import Any


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Lowercase, strip, and replace spaces/special characters in column names.
    
    Args:
        df: Input DataFrame with potentially messy column names
        
    Returns:
        DataFrame with normalized column names
    """
    df = df.copy()
    df.columns = [
        re.sub(r'[^a-z0-9]+', '_', col.lower().strip()).strip('_')
        for col in df.columns
    ]
    return df


def compute_week_start(d: pd.Timestamp | datetime | date) -> date:
    """
    Given a date or timestamp, return the Monday representing the start of that week.
    
    Args:
        d: Input date/timestamp
        
    Returns:
        Date object representing the Monday of that week
    """
    if isinstance(d, pd.Timestamp):
        d = d.date()
    elif isinstance(d, datetime):
        d = d.date()
    
    # Get the weekday (0 = Monday, 6 = Sunday)
    days_since_monday = d.weekday()
    week_start = d - timedelta(days=days_since_monday)
    return week_start


def parse_amount(value: Any) -> float | None:
    """
    Parse various amount formats (with commas, parentheses, currency symbols).
    
    Args:
        value: Input value that might be string, float, int, etc.
        
    Returns:
        Parsed float value or None if invalid
    """
    if pd.isna(value):
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remove currency symbols, commas, spaces
        cleaned = re.sub(r'[₹$,\s]', '', value.strip())
        
        # Handle parentheses as negative (accounting notation)
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    return None


def find_matching_column(df: pd.DataFrame, possible_names: list[str]) -> str | None:
    """
    Find the first matching column name from a list of possibilities.
    
    Args:
        df: Input DataFrame
        possible_names: List of possible column names to look for
        
    Returns:
        Actual column name if found, None otherwise
    """
    df_cols = [col.lower() for col in df.columns]
    
    for name in possible_names:
        if name.lower() in df_cols:
            return df.columns[df_cols.index(name.lower())]
    
    return None
