"""
Advanced dynamic features for FlexiCoach - Real-time insights and gamification.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np


def calculate_financial_momentum(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate financial momentum - are habits improving or declining?
    """
    if len(df) < 7:
        return {"momentum": "neutral", "score": 50, "message": "Need more data to calculate momentum"}
    
    df = df.sort_values('date')
    
    # Split data into two halves
    mid_point = len(df) // 2
    first_half = df.iloc[:mid_point]
    second_half = df.iloc[mid_point:]
    
    # Calculate average daily spending for each half
    first_avg = first_half[first_half['is_expense']]['amount'].sum() / len(first_half)
    second_avg = second_half[second_half['is_expense']]['amount'].sum() / len(second_half)
    
    # Calculate percentage change
    if first_avg > 0:
        change = ((first_avg - second_avg) / first_avg) * 100
    else:
        change = 0
    
    # Calculate savings rate for each half
    first_income = first_half[~first_half['is_expense']]['amount'].sum()
    first_expense = first_half[first_half['is_expense']]['amount'].sum()
    second_income = second_half[~second_half['is_expense']]['amount'].sum()
    second_expense = second_half[second_half['is_expense']]['amount'].sum()
    
    first_savings_rate = ((first_income - first_expense) / first_income * 100) if first_income > 0 else 0
    second_savings_rate = ((second_income - second_expense) / second_income * 100) if second_income > 0 else 0
    
    savings_improvement = second_savings_rate - first_savings_rate
    
    # Calculate momentum score (0-100)
    momentum_score = 50 + (change / 2) + (savings_improvement / 2)
    momentum_score = max(0, min(100, momentum_score))
    
    if momentum_score >= 70:
        momentum = "🚀 Strong Upward"
        message = "Excellent! Your spending habits are improving significantly."
        emoji = "🚀"
    elif momentum_score >= 55:
        momentum = "📈 Positive"
        message = "Good progress! Keep maintaining these habits."
        emoji = "📈"
    elif momentum_score >= 45:
        momentum = "➡️ Stable"
        message = "Your habits are stable. Look for improvement opportunities."
        emoji = "➡️"
    else:
        momentum = "📉 Needs Attention"
        message = "Time to review and adjust your spending patterns."
        emoji = "📉"
    
    return {
        "momentum": momentum,
        "score": round(momentum_score, 1),
        "emoji": emoji,
        "message": message,
        "spending_change": round(change, 1),
        "savings_improvement": round(savings_improvement, 1)
    }


def detect_spending_triggers(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Identify what triggers excessive spending (day of week, time patterns).
    """
    if len(df) < 10:
        return {"triggers": []}
    
    df = df[df['is_expense']].copy()
    df['day_of_week'] = df['date'].dt.day_name()
    df['is_weekend'] = df['date'].dt.dayofweek >= 5
    df['week_number'] = df['date'].dt.isocalendar().week
    
    triggers = []
    
    # Day of week analysis
    daily_spending = df.groupby('day_of_week')['amount'].agg(['sum', 'mean', 'count'])
    avg_daily = df['amount'].mean()
    
    for day, row in daily_spending.iterrows():
        if row['mean'] > avg_daily * 1.3 and row['count'] >= 2:
            triggers.append({
                "type": "High Spending Day",
                "trigger": day,
                "impact": f"₹{row['mean']:.0f}/transaction (30% above average)",
                "recommendation": f"Plan ahead for {day}s - pack lunch or limit eating out"
            })
    
    # Weekend vs weekday
    weekend_avg = df[df['is_weekend']]['amount'].mean()
    weekday_avg = df[~df['is_weekend']]['amount'].mean()
    
    if weekend_avg > weekday_avg * 1.4:
        triggers.append({
            "type": "Weekend Splurge",
            "trigger": "Weekends",
            "impact": f"₹{weekend_avg - weekday_avg:.0f} more per transaction",
            "recommendation": "Set a weekend budget or plan free/low-cost activities"
        })
    
    # Impulse spending detection (multiple small transactions same day)
    same_day_txns = df.groupby(df['date'].dt.date).size()
    impulse_days = same_day_txns[same_day_txns >= 4].count()
    
    if impulse_days >= 2:
        triggers.append({
            "type": "Impulse Spending Pattern",
            "trigger": "Multiple transactions per day",
            "impact": f"{impulse_days} days with 4+ transactions",
            "recommendation": "Use the 24-hour rule: wait before non-essential purchases"
        })
    
    return {
        "triggers": triggers,
        "total_triggers": len(triggers)
    }


def generate_smart_challenges(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Gamified challenges based on user's spending patterns.
    """
    challenges = []
    
    if len(df) < 5:
        return challenges
    
    df_expenses = df[df['is_expense']].copy()
    
    # Calculate current metrics
    daily_avg = df_expenses['amount'].mean()
    total_monthly = df_expenses['amount'].sum()
    
    # Challenge 1: No-Spend Days
    df_daily = df_expenses.groupby(df_expenses['date'].dt.date).size()
    spending_days = len(df_daily)
    total_days = (df['date'].max() - df['date'].min()).days + 1
    no_spend_days = total_days - spending_days
    
    challenges.append({
        "id": "no_spend_days",
        "title": "🎯 No-Spend Challenge",
        "description": f"You have {no_spend_days} no-spend days. Try for {no_spend_days + 3} this month!",
        "target": no_spend_days + 3,
        "current": no_spend_days,
        "reward": "₹300 monthly savings",
        "difficulty": "Medium",
        "points": 150
    })
    
    # Challenge 2: Eating Out Reduction
    food_keywords = ['zomato', 'swiggy', 'restaurant', 'cafe', 'coffee', 'pizza', 'food']
    food_txns = df_expenses[df_expenses['description'].str.lower().str.contains('|'.join(food_keywords), na=False)]
    
    if len(food_txns) >= 3:
        food_weekly = len(food_txns) / (total_days / 7)
        target = max(1, int(food_weekly * 0.7))
        
        challenges.append({
            "id": "reduce_eating_out",
            "title": "🍳 Home Chef Challenge",
            "description": f"You order food {int(food_weekly)} times/week. Reduce to {target} times!",
            "target": target,
            "current": int(food_weekly),
            "reward": f"₹{int(food_txns['amount'].sum() * 0.3)} monthly savings",
            "difficulty": "Easy",
            "points": 100
        })
    
    # Challenge 3: Micro-saving (Round up challenge)
    total_transactions = len(df_expenses)
    potential_roundup = (np.ceil(df_expenses['amount']) - df_expenses['amount']).sum()
    
    challenges.append({
        "id": "round_up_savings",
        "title": "💰 Round-Up Saver",
        "description": "Round up every purchase to nearest ₹10 and save the difference",
        "target": round(potential_roundup, 2),
        "current": 0,
        "reward": f"₹{int(potential_roundup)} painless savings",
        "difficulty": "Easy",
        "points": 75
    })
    
    # Challenge 4: Daily Spending Limit
    daily_limit = daily_avg * 0.85
    
    challenges.append({
        "id": "daily_limit",
        "title": "📊 Daily Budget Master",
        "description": f"Stay under ₹{int(daily_limit)} per day for 7 consecutive days",
        "target": 7,
        "current": 0,
        "reward": "₹500 monthly savings + Streaker Badge",
        "difficulty": "Hard",
        "points": 200
    })
    
    # Challenge 5: Category Cut (biggest spending category)
    if 'category' in df_expenses.columns:
        top_category = df_expenses.groupby('category')['amount'].sum().idxmax()
        category_total = df_expenses[df_expenses['category'] == top_category]['amount'].sum()
        
        challenges.append({
            "id": "category_reduction",
            "title": f"✂️ Cut {top_category.title()} by 20%",
            "description": f"Your {top_category} spending is ₹{int(category_total)}. Reduce by 20%!",
            "target": int(category_total * 0.8),
            "current": int(category_total),
            "reward": f"₹{int(category_total * 0.2)} savings",
            "difficulty": "Medium",
            "points": 175
        })
    
    return challenges


def calculate_financial_personality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Determine user's financial personality type based on behavior.
    """
    if len(df) < 10:
        return {"personality": "New User", "traits": []}
    
    df_expenses = df[df['is_expense']].copy()
    
    # Calculate various metrics
    total_expense = df_expenses['amount'].sum()
    avg_transaction = df_expenses['amount'].mean()
    std_transaction = df_expenses['amount'].std()
    num_transactions = len(df_expenses)
    
    # Variability ratio
    cv = (std_transaction / avg_transaction) if avg_transaction > 0 else 0
    
    # Large transaction ratio
    large_threshold = avg_transaction * 2
    large_txns = len(df_expenses[df_expenses['amount'] > large_threshold])
    large_ratio = large_txns / num_transactions if num_transactions > 0 else 0
    
    # Frequency
    days_range = (df['date'].max() - df['date'].min()).days + 1
    txn_per_day = num_transactions / days_range
    
    # Determine personality
    traits = []
    
    if cv < 0.5:
        personality = "The Consistent Planner"
        traits = [
            "Predictable spending patterns",
            "Good at budgeting",
            "Rarely makes impulse purchases",
            "Prefers routine expenses"
        ]
        emoji = "📋"
        advice = "Your consistency is admirable! Try automating savings to maximize this strength."
        
    elif cv > 1.5 and large_ratio > 0.2:
        personality = "The Spontaneous Spender"
        traits = [
            "Variable spending habits",
            "Makes occasional big purchases",
            "Flexible with budget",
            "Enjoys spontaneous decisions"
        ]
        emoji = "🎲"
        advice = "Your flexibility is good, but consider setting aside an 'impulse fund' to protect savings."
        
    elif txn_per_day > 2:
        personality = "The Frequent Shopper"
        traits = [
            "High transaction frequency",
            "Prefers multiple small purchases",
            "Active spender",
            "Enjoys variety"
        ]
        emoji = "🛍️"
        advice = "Try consolidating purchases to reduce transaction fees and save time!"
        
    elif avg_transaction > total_expense / num_transactions * 1.5:
        personality = "The Bulk Buyer"
        traits = [
            "Prefers larger purchases",
            "Plans ahead",
            "Shops less frequently",
            "Values convenience"
        ]
        emoji = "📦"
        advice = "Your bulk buying is smart! Ensure you're actually saving vs. buying unnecessary quantities."
        
    else:
        personality = "The Balanced Spender"
        traits = [
            "Moderate spending patterns",
            "Mix of small and large purchases",
            "Balanced approach",
            "Adaptable habits"
        ]
        emoji = "⚖️"
        advice = "Your balanced approach is great! Focus on optimizing each spending category."
    
    return {
        "personality": personality,
        "emoji": emoji,
        "traits": traits,
        "advice": advice,
        "spending_variability": round(cv, 2),
        "transaction_frequency": round(txn_per_day, 2)
    }


def generate_peer_comparison(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Anonymous peer comparison based on income brackets.
    """
    df_income = df[~df['is_expense']]['amount'].sum()
    df_expense = df[df['is_expense']]['amount'].sum()
    
    savings_rate = ((df_income - df_expense) / df_income * 100) if df_income > 0 else 0
    
    # Simulated peer data (in production, this would be from anonymized user database)
    if df_income < 30000:
        bracket = "₹0-30K/month"
        peer_avg_savings = 12
        peer_avg_expense = 25000
    elif df_income < 50000:
        bracket = "₹30-50K/month"
        peer_avg_savings = 18
        peer_avg_expense = 38000
    elif df_income < 75000:
        bracket = "₹50-75K/month"
        peer_avg_savings = 22
        peer_avg_expense = 55000
    else:
        bracket = "₹75K+/month"
        peer_avg_savings = 28
        peer_avg_expense = 70000
    
    percentile = 50
    if savings_rate > peer_avg_savings * 1.3:
        percentile = 85
        rank = "Top 15%"
    elif savings_rate > peer_avg_savings * 1.1:
        percentile = 70
        rank = "Top 30%"
    elif savings_rate > peer_avg_savings * 0.9:
        percentile = 50
        rank = "Average"
    else:
        percentile = 30
        rank = "Below Average"
    
    return {
        "income_bracket": bracket,
        "your_savings_rate": round(savings_rate, 1),
        "peer_avg_savings_rate": peer_avg_savings,
        "your_monthly_expense": round(df_expense, 2),
        "peer_avg_expense": peer_avg_expense,
        "percentile": percentile,
        "rank": rank,
        "insight": f"You're saving {abs(round(savings_rate - peer_avg_savings, 1))}% {'more' if savings_rate > peer_avg_savings else 'less'} than peers in your bracket"
    }


def calculate_money_habits_score(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Comprehensive money habits scoring system (different from health score).
    """
    scores = {}
    
    # 1. Consistency Score (0-20)
    df_expenses = df[df['is_expense']].copy()
    if len(df_expenses) >= 7:
        daily_variance = df_expenses.groupby(df_expenses['date'].dt.date)['amount'].sum().std()
        daily_mean = df_expenses.groupby(df_expenses['date'].dt.date)['amount'].sum().mean()
        cv = (daily_variance / daily_mean) if daily_mean > 0 else 1
        consistency_score = max(0, 20 - (cv * 10))
    else:
        consistency_score = 10
    
    # 2. Mindfulness Score (0-20) - based on transaction frequency
    days_range = (df['date'].max() - df['date'].min()).days + 1
    txn_per_day = len(df_expenses) / days_range if days_range > 0 else 0
    mindfulness_score = 20 if txn_per_day <= 1.5 else max(0, 20 - ((txn_per_day - 1.5) * 5))
    
    # 3. Planning Score (0-20) - no-spend days indicate planning
    spending_days = df_expenses['date'].dt.date.nunique()
    no_spend_ratio = (days_range - spending_days) / days_range if days_range > 0 else 0
    planning_score = no_spend_ratio * 20
    
    # 4. Impulse Control (0-20) - based on large unexpected purchases
    median_txn = df_expenses['amount'].median()
    large_txns = len(df_expenses[df_expenses['amount'] > median_txn * 3])
    impulse_score = max(0, 20 - (large_txns * 2))
    
    # 5. Savings Discipline (0-20)
    income = df[~df['is_expense']]['amount'].sum()
    expense = df_expenses['amount'].sum()
    savings_rate = ((income - expense) / income * 100) if income > 0 else 0
    savings_score = min(20, savings_rate)
    
    total_score = consistency_score + mindfulness_score + planning_score + impulse_score + savings_score
    
    return {
        "total_score": round(total_score, 1),
        "max_score": 100,
        "breakdown": {
            "consistency": round(consistency_score, 1),
            "mindfulness": round(mindfulness_score, 1),
            "planning": round(planning_score, 1),
            "impulse_control": round(impulse_score, 1),
            "savings_discipline": round(savings_score, 1)
        },
        "grade": "A+" if total_score >= 90 else "A" if total_score >= 80 else "B" if total_score >= 70 else "C" if total_score >= 60 else "D",
        "message": "Excellent money habits!" if total_score >= 80 else "Good habits with room for improvement" if total_score >= 60 else "Focus on building stronger habits"
    }
