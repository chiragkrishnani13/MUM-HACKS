"""
Budget planning and financial insights generation.
"""

import pandas as pd
from typing import Dict, List, Any
from utils.helpers import compute_week_start


def generate_budget_plan(df: pd.DataFrame) -> dict:
    """
    Generate an overall budget and insights from the labeled transactions.
    
    Computes:
    - Income, expenses, needs, wants, savings potential
    - Suggested weekly budget based on historical spending
    - Category-wise spending breakdown
    - Weekly spending time series
    - Rule-based financial flags and insights
    
    Args:
        df: Labeled DataFrame with columns:
            'date' (datetime), 'amount' (float), 'is_expense' (bool),
            'category' (str), 'need_vs_want' (str)
    
    Returns:
        Dictionary with structure:
        {
          "summary": { ... },
          "categories": [ ... ],
          "weekly_series": [ ... ],
          "flags": [ ... ]
        }
    """
    if df.empty:
        raise ValueError("Cannot generate budget plan from empty DataFrame")
    
    # Compute totals
    total_income = df[~df['is_expense']]['amount'].sum()
    total_expenses = df[df['is_expense']]['amount'].sum()
    total_needs = df[df['need_vs_want'] == 'need']['amount'].sum()
    total_wants = df[df['need_vs_want'] == 'want']['amount'].sum()
    savings_potential = total_income - total_expenses
    
    # Compute time range
    min_date = df['date'].min()
    max_date = df['date'].max()
    days_range = (max_date - min_date).days
    num_weeks = max(1, days_range / 7)
    
    # Suggested weekly budget (average weekly expenses)
    suggested_weekly_budget = total_expenses / num_weeks if num_weeks > 0 else total_expenses
    
    # Category-wise breakdown (expenses only)
    expenses_df = df[df['is_expense']].copy()
    category_summary = expenses_df.groupby('category')['amount'].sum().reset_index()
    category_summary = category_summary.sort_values('amount', ascending=False)
    
    categories = [
        {"name": row['category'], "amount": round(row['amount'], 2)}
        for _, row in category_summary.iterrows()
    ]
    
    # Weekly spending time series
    expenses_df['week_start'] = expenses_df['date'].apply(compute_week_start)
    weekly_spending = expenses_df.groupby('week_start')['amount'].sum().reset_index()
    weekly_spending = weekly_spending.sort_values('week_start')
    
    weekly_series = [
        {
            "week_start": row['week_start'].strftime('%Y-%m-%d'),
            "total_spent": round(row['amount'], 2)
        }
        for _, row in weekly_spending.iterrows()
    ]
    
    # Generate flags (insights)
    flags = []
    
    # Savings potential
    if savings_potential < 0:
        flags.append(f"⚠️ You're spending ₹{abs(round(savings_potential, 2))} more than your income. Time to cut back!")
    elif savings_potential > 0:
        savings_rate = (savings_potential / total_income * 100) if total_income > 0 else 0
        flags.append(f"✅ Great! You have ₹{round(savings_potential, 2)} savings potential ({round(savings_rate, 1)}% of income).")
    
    # Needs vs wants balance
    if total_expenses > 0:
        wants_percentage = (total_wants / total_expenses) * 100
        if wants_percentage > 50:
            flags.append(f"💸 {round(wants_percentage, 1)}% of your spending is on 'wants'. Consider reducing discretionary expenses.")
        elif wants_percentage < 20:
            flags.append(f"👍 You're being disciplined - only {round(wants_percentage, 1)}% on wants. Keep it up!")
    
    # High concentration in single category
    if not category_summary.empty and total_expenses > 0:
        top_category = category_summary.iloc[0]
        concentration = (top_category['amount'] / total_expenses) * 100
        if concentration > 40:
            flags.append(f"📊 High spending concentration: {round(concentration, 1)}% of expenses are in '{top_category['category']}'.")
    
    # Weekly volatility check
    if len(weekly_spending) > 1:
        weekly_std = weekly_spending['amount'].std()
        weekly_mean = weekly_spending['amount'].mean()
        if weekly_mean > 0 and (weekly_std / weekly_mean) > 0.5:
            flags.append("📈 Your weekly spending varies significantly. Try to maintain more consistent spending patterns.")
    
    # Emergency fund suggestion
    if total_income > 0:
        monthly_expenses = total_expenses * (30 / days_range) if days_range > 0 else total_expenses
        if savings_potential > 0 and savings_potential < monthly_expenses:
            flags.append(f"🎯 Goal: Build an emergency fund covering 3-6 months of expenses (₹{round(monthly_expenses * 3, 2)} - ₹{round(monthly_expenses * 6, 2)}).")
    
    # If no flags generated, add a generic positive note
    if not flags:
        flags.append("📝 Keep tracking your expenses regularly to identify more insights!")
    
    # Build summary
    summary = {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "total_needs": round(total_needs, 2),
        "total_wants": round(total_wants, 2),
        "savings_potential": round(savings_potential, 2),
        "suggested_weekly_budget": round(suggested_weekly_budget, 2)
    }
    
    return {
        "summary": summary,
        "categories": categories,
        "weekly_series": weekly_series,
        "flags": flags
    }
