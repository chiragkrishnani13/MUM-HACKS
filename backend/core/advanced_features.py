"""
Advanced financial analysis features.
"""

import pandas as pd
from typing import Dict, List, Any
from datetime import datetime, timedelta


def detect_spending_patterns(df: pd.DataFrame) -> dict:
    """
    Detect spending patterns and anomalies using ML-inspired heuristics.
    
    Features:
    - Day of week spending patterns
    - Time-based spending trends
    - Unusual transaction detection
    - Spending streaks (consecutive days)
    """
    if df.empty:
        return {}
    
    expenses = df[df['is_expense']].copy()
    
    # Day of week analysis
    expenses['day_of_week'] = expenses['date'].dt.day_name()
    dow_spending = expenses.groupby('day_of_week')['amount'].agg(['sum', 'count']).to_dict('index')
    
    # Find highest spending days
    dow_sums = {day: info['sum'] for day, info in dow_spending.items()}
    highest_day = max(dow_sums, key=dow_sums.get) if dow_sums else None
    
    # Detect spending streaks
    expenses_sorted = expenses.sort_values('date')
    dates = expenses_sorted['date'].dt.date.unique()
    
    max_streak = 1
    current_streak = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1
    
    # Detect large transactions (outliers)
    if len(expenses) > 5:
        q75 = expenses['amount'].quantile(0.75)
        q25 = expenses['amount'].quantile(0.25)
        iqr = q75 - q25
        upper_bound = q75 + (1.5 * iqr)
        
        large_transactions = expenses[expenses['amount'] > upper_bound]
        outliers = [
            {
                "date": row['date'].strftime('%Y-%m-%d'),
                "description": row['description'][:50],
                "amount": round(row['amount'], 2),
                "category": row['category']
            }
            for _, row in large_transactions.head(5).iterrows()
        ]
    else:
        outliers = []
    
    return {
        "highest_spending_day": highest_day,
        "longest_spending_streak": max_streak,
        "large_transactions": outliers,
        "day_of_week_pattern": {
            day: round(info['sum'], 2) 
            for day, info in dow_spending.items()
        }
    }


def predict_next_month(df: pd.DataFrame) -> dict:
    """
    Predict next month's expenses based on historical patterns.
    """
    if df.empty:
        return {}
    
    expenses = df[df['is_expense']].copy()
    
    # Calculate daily average
    date_range = (df['date'].max() - df['date'].min()).days
    if date_range < 7:
        return {"prediction": "Need more data (at least 2 weeks)"}
    
    total_expenses = expenses['amount'].sum()
    daily_avg = total_expenses / max(date_range, 1)
    monthly_prediction = daily_avg * 30
    
    # Category-wise predictions
    category_monthly = {}
    for category in expenses['category'].unique():
        cat_expenses = expenses[expenses['category'] == category]['amount'].sum()
        cat_monthly = (cat_expenses / date_range) * 30
        category_monthly[category] = round(cat_monthly, 2)
    
    return {
        "predicted_monthly_expenses": round(monthly_prediction, 2),
        "daily_average": round(daily_avg, 2),
        "category_predictions": category_monthly,
        "confidence": "Medium" if date_range > 30 else "Low"
    }


def compare_to_benchmarks(df: pd.DataFrame) -> dict:
    """
    Compare user's spending to recommended benchmarks (50/30/20 rule).
    """
    if df.empty:
        return {}
    
    total_income = df[~df['is_expense']]['amount'].sum()
    total_needs = df[df['need_vs_want'] == 'need']['amount'].sum()
    total_wants = df[df['need_vs_want'] == 'want']['amount'].sum()
    
    if total_income == 0:
        return {"message": "No income data available for comparison"}
    
    needs_percent = (total_needs / total_income) * 100
    wants_percent = (total_wants / total_income) * 100
    savings_percent = ((total_income - total_needs - total_wants) / total_income) * 100
    
    # 50/30/20 rule: 50% needs, 30% wants, 20% savings
    return {
        "your_split": {
            "needs": round(needs_percent, 1),
            "wants": round(wants_percent, 1),
            "savings": round(savings_percent, 1)
        },
        "ideal_split": {
            "needs": 50,
            "wants": 30,
            "savings": 20
        },
        "comparison": {
            "needs": "✅ Good" if needs_percent <= 55 else "⚠️ High",
            "wants": "✅ Good" if wants_percent <= 35 else "⚠️ High",
            "savings": "✅ Great" if savings_percent >= 15 else "⚠️ Low"
        }
    }


def generate_savings_goals(df: pd.DataFrame) -> List[dict]:
    """
    Generate personalized savings goals based on spending patterns.
    """
    if df.empty:
        return []
    
    expenses = df[df['is_expense']].copy()
    total_income = df[~df['is_expense']]['amount'].sum()
    total_expenses = expenses['amount'].sum()
    wants = df[df['need_vs_want'] == 'want']['amount'].sum()
    
    goals = []
    
    # Emergency fund goal
    monthly_expenses = total_expenses / max(1, (df['date'].max() - df['date'].min()).days / 30)
    emergency_target = monthly_expenses * 3
    current_savings = total_income - total_expenses
    
    if current_savings < emergency_target:
        goals.append({
            "type": "Emergency Fund",
            "target": round(emergency_target, 2),
            "current": round(max(0, current_savings), 2),
            "timeline": "6-12 months",
            "priority": "High"
        })
    
    # Reduce wants by 10%
    if wants > 0:
        reduce_target = wants * 0.10
        goals.append({
            "type": "Reduce Discretionary Spending",
            "target": round(reduce_target, 2),
            "description": "Save by cutting wants by 10%",
            "timeline": "1 month",
            "priority": "Medium"
        })
    
    # Category-specific goals
    food_want = expenses[(expenses['category'] == 'food') & (expenses['need_vs_want'] == 'want')]['amount'].sum()
    if food_want > monthly_expenses * 0.15:
        goals.append({
            "type": "Cook More at Home",
            "target": round(food_want * 0.3, 2),
            "description": "Save 30% on eating out",
            "timeline": "1 month",
            "priority": "Medium"
        })
    
    return goals


def financial_health_score(df: pd.DataFrame) -> dict:
    """
    Calculate overall financial health score (0-100).
    """
    if df.empty:
        return {"score": 0, "message": "No data"}
    
    score = 0
    factors = []
    
    total_income = df[~df['is_expense']]['amount'].sum()
    total_expenses = df[df['is_expense']]['amount'].sum()
    total_wants = df[df['need_vs_want'] == 'want']['amount'].sum()
    
    # Factor 1: Savings rate (30 points)
    if total_income > 0:
        savings_rate = ((total_income - total_expenses) / total_income) * 100
        if savings_rate >= 20:
            score += 30
            factors.append("✅ Excellent savings rate")
        elif savings_rate >= 10:
            score += 20
            factors.append("👍 Good savings rate")
        elif savings_rate >= 0:
            score += 10
            factors.append("⚠️ Low savings rate")
        else:
            factors.append("❌ Spending exceeds income")
    
    # Factor 2: Wants control (25 points)
    if total_expenses > 0:
        wants_ratio = (total_wants / total_expenses) * 100
        if wants_ratio <= 30:
            score += 25
            factors.append("✅ Well-controlled discretionary spending")
        elif wants_ratio <= 50:
            score += 15
            factors.append("⚠️ Moderate discretionary spending")
        else:
            score += 5
            factors.append("❌ High discretionary spending")
    
    # Factor 3: Spending consistency (20 points)
    expenses = df[df['is_expense']].copy()
    if len(expenses) > 7:
        expenses['week'] = expenses['date'].dt.isocalendar().week
        weekly_variance = expenses.groupby('week')['amount'].sum().std()
        weekly_mean = expenses.groupby('week')['amount'].sum().mean()
        
        if weekly_mean > 0:
            cv = weekly_variance / weekly_mean
            if cv < 0.3:
                score += 20
                factors.append("✅ Consistent spending patterns")
            elif cv < 0.6:
                score += 10
                factors.append("⚠️ Some spending volatility")
            else:
                factors.append("❌ Highly variable spending")
    
    # Factor 4: Emergency buffer (25 points)
    monthly_expenses = total_expenses / max(1, (df['date'].max() - df['date'].min()).days / 30)
    potential_buffer = (total_income - total_expenses) / monthly_expenses
    
    if potential_buffer >= 3:
        score += 25
        factors.append("✅ Strong emergency buffer")
    elif potential_buffer >= 1:
        score += 15
        factors.append("👍 Decent emergency buffer")
    else:
        score += 5
        factors.append("⚠️ Build emergency fund")
    
    # Health rating
    if score >= 80:
        rating = "Excellent"
        emoji = "🌟"
    elif score >= 60:
        rating = "Good"
        emoji = "👍"
    elif score >= 40:
        rating = "Fair"
        emoji = "⚠️"
    else:
        rating = "Needs Improvement"
        emoji = "📈"
    
    return {
        "score": score,
        "rating": rating,
        "emoji": emoji,
        "factors": factors
    }
