"""
Transaction classification into categories and needs vs wants.
"""

import pandas as pd


def infer_category(description: str, is_expense: bool) -> tuple[str, str]:
    """
    Infer category and need_vs_want classification from transaction description.
    
    Args:
        description: Transaction description text
        is_expense: Whether this is an expense (True) or income (False)
        
    Returns:
        Tuple of (category, need_vs_want)
    """
    desc_lower = description.lower()
    
    # Income transactions
    if not is_expense:
        return ('income', 'income')
    
    # Rent/Housing (need)
    if any(word in desc_lower for word in ['rent', 'lease', 'emi', 'loan', 'mortgage', 'housing']):
        return ('rent', 'need')
    
    # Groceries (need)
    if any(word in desc_lower for word in ['grocery', 'supermarket', 'kirana', 'vegetable', 'fruit', 'dmart', 'reliance fresh', 'big bazaar']):
        return ('food', 'need')
    
    # Food - eating out (want)
    if any(word in desc_lower for word in ['zomato', 'swiggy', 'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'domino', 'mcdonald', 'kfc', 'food delivery']):
        return ('food', 'want')
    
    # Transport (need - usually commuting)
    if any(word in desc_lower for word in ['uber', 'ola', 'bus', 'train', 'metro', 'fuel', 'petrol', 'diesel', 'gas', 'rapido', 'auto']):
        return ('transport', 'need')
    
    # Bills/Utilities (need)
    if any(word in desc_lower for word in ['electricity', 'water', 'wifi', 'internet', 'phone', 'mobile', 'recharge', 'gas', 'cylinder', 'utility', 'bill payment']):
        return ('bills', 'need')
    
    # Health/Medical (need)
    if any(word in desc_lower for word in ['medical', 'hospital', 'doctor', 'pharmacy', 'medicine', 'health', 'insurance', 'apollo', 'medicare']):
        return ('health', 'need')
    
    # Entertainment (want)
    if any(word in desc_lower for word in ['netflix', 'spotify', 'amazon prime', 'hotstar', 'movie', 'cinema', 'theatre', 'pvr', 'inox', 'gaming', 'game']):
        return ('entertainment', 'want')
    
    # Shopping (want)
    if any(word in desc_lower for word in ['amazon', 'flipkart', 'myntra', 'ajio', 'shopping', 'mall', 'store', 'fashion', 'clothing', 'shoes']):
        return ('shopping', 'want')
    
    # Education (need)
    if any(word in desc_lower for word in ['education', 'school', 'college', 'university', 'course', 'tuition', 'book', 'study']):
        return ('education', 'need')
    
    # Default: other (want for safety - encourages scrutiny)
    return ('other', 'want')


def classify_spending(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add classification columns to the DataFrame.
    
    Adds:
    - 'category': coarse category (rent, food, transport, bills, shopping, entertainment, health, income, other)
    - 'need_vs_want': either 'need', 'want', or 'income'
    
    Uses simple keyword-based heuristics on the 'description' column.
    
    Args:
        df: Cleaned DataFrame with 'description' and 'is_expense' columns
        
    Returns:
        Same DataFrame with two new columns: 'category' and 'need_vs_want'
    """
    df = df.copy()
    
    # Apply classification to each row
    classifications = df.apply(
        lambda row: infer_category(row['description'], row['is_expense']),
        axis=1
    )
    
    df['category'] = classifications.apply(lambda x: x[0])
    df['need_vs_want'] = classifications.apply(lambda x: x[1])
    
    return df
