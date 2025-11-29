"""
Data cleaning and normalization for transaction data.
"""

import pandas as pd
from typing import Any
from utils.helpers import normalize_column_names, parse_amount, find_matching_column


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize the raw transactions DataFrame.
    
    Responsibilities:
    - Normalize column names (lower-case, strip spaces, replace special chars with underscores).
    - Ensure required columns exist: "date", "description", "amount".
    - Parse dates into datetime.
    - Convert amount to numeric (handle commas, parentheses, etc.).
    - Standardize expenses as positive numbers with an "is_expense" column (bool).
    - Drop rows with missing or invalid amount/date.
    
    Args:
        df: Raw transactions DataFrame from CSV upload
        
    Returns:
        Cleaned DataFrame with columns: ["date", "description", "amount", "is_expense"]
    """
    if df.empty:
        raise ValueError("Empty DataFrame provided")
    
    # Normalize column names
    df = normalize_column_names(df)
    
    # Find required columns by trying multiple possible names
    date_col = find_matching_column(df, [
        'date', 'transaction_date', 'txn_date', 'trans_date', 
        'posting_date', 'value_date', 'timestamp'
    ])
    
    desc_col = find_matching_column(df, [
        'description', 'narration', 'particulars', 'details', 
        'transaction_details', 'remarks', 'memo'
    ])
    
    amount_col = find_matching_column(df, [
        'amount', 'transaction_amount', 'value', 'debit', 
        'credit', 'txn_amount'
    ])
    
    if not date_col:
        raise ValueError("No date column found in CSV. Expected columns like 'date', 'transaction_date', etc.")
    if not desc_col:
        raise ValueError("No description column found in CSV. Expected columns like 'description', 'narration', etc.")
    if not amount_col:
        raise ValueError("No amount column found in CSV. Expected columns like 'amount', 'transaction_amount', etc.")
    
    # Create working DataFrame with normalized names
    df_clean = pd.DataFrame()
    df_clean['date'] = df[date_col]
    df_clean['description'] = df[desc_col].fillna('').astype(str)
    df_clean['amount_raw'] = df[amount_col]
    
    # Parse dates
    try:
        df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')
    except Exception as e:
        raise ValueError(f"Failed to parse date column: {e}")
    
    # Parse amounts
    df_clean['amount'] = df_clean['amount_raw'].apply(parse_amount)
    
    # Drop rows with invalid date or amount
    rows_before = len(df_clean)
    df_clean = df_clean.dropna(subset=['date', 'amount'])
    rows_after = len(df_clean)
    
    if rows_before > rows_after:
        print(f"Warning: Dropped {rows_before - rows_after} rows with invalid date/amount")
    
    if df_clean.empty:
        raise ValueError(f"No valid transactions found after cleaning. Original CSV had {len(df)} rows. Check if dates and amounts are in correct format.")
    
    # Determine if transaction is expense or income
    # Strategy: Check for debit/credit columns, or infer from amount sign
    # Look for separate debit/credit columns
    debit_col = find_matching_column(df, ['debit', 'debit_amount', 'withdrawal'])
    credit_col = find_matching_column(df, ['credit', 'credit_amount', 'deposit'])
    
    if debit_col and credit_col:
        # We have separate columns - reconstruct logic
        df_clean['is_expense'] = pd.notna(df[debit_col]) & (df[debit_col] != 0)
        # Make all amounts positive
        df_clean['amount'] = df_clean['amount'].abs()
    else:
        # Infer from sign: negative = expense (money going out)
        # But some banks use positive for expenses, so we'll use a heuristic:
        # If most values are positive, assume positive = expense
        # If mostly negative, assume negative = expense
        
        positive_count = (df_clean['amount'] > 0).sum()
        negative_count = (df_clean['amount'] < 0).sum()
        
        if negative_count > positive_count:
            # Negative = expense
            df_clean['is_expense'] = df_clean['amount'] < 0
            df_clean['amount'] = df_clean['amount'].abs()
        else:
            # Check for keywords in description to identify income
            income_keywords = ['salary', 'credit', 'deposit', 'refund', 'cashback', 'interest earned']
            df_clean['is_expense'] = True  # Default to expense
            
            for keyword in income_keywords:
                mask = df_clean['description'].str.lower().str.contains(keyword, na=False)
                df_clean.loc[mask, 'is_expense'] = False
            
            # Make all amounts positive
            df_clean['amount'] = df_clean['amount'].abs()
    
    # Final cleanup
    df_clean = df_clean[['date', 'description', 'amount', 'is_expense']].copy()
    df_clean = df_clean.sort_values('date').reset_index(drop=True)
    
    return df_clean
