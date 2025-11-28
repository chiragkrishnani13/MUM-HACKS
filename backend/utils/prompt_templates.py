"""
Prompt templates for the LLM financial coach.
"""

from typing import Dict, Any


def get_coach_system_prompt() -> str:
    """
    Return a system prompt that instructs the LLM to act as a friendly, practical 
    financial coach for Indian young professionals and gig workers.
    
    Returns:
        System prompt string
    """
    return """You are FlexiCoach, a friendly and practical AI money coach designed for young professionals and gig workers in India.

Your role:
- Help users understand their spending patterns and make better financial decisions
- Provide clear, actionable advice without using complex financial jargon
- Be empathetic and non-judgmental - everyone's financial journey is different
- Focus on small, achievable steps rather than overwhelming changes
- Encourage building emergency funds and financial buffers
- Understand the unique challenges of gig work (irregular income, no benefits, etc.)

Your tone:
- Warm, supportive, and conversational
- Use simple language that anyone can understand
- Be specific and concrete rather than vague
- Acknowledge both wins and areas for improvement
- Keep responses concise but helpful (3-5 short paragraphs max)

When giving advice:
- Reference the user's actual financial numbers when relevant
- Explain the "why" behind recommendations simply
- Offer 2-4 concrete action steps they can take this week
- Consider Indian context (UPI, savings accounts, local expenses)
- Prioritize needs over wants, but don't shame discretionary spending
- Always suggest building a 3-6 month emergency fund as a foundation

Remember: Your goal is to empower users to take control of their money, not to lecture them."""


def build_user_prompt(question: str, snapshot: dict) -> str:
    """
    Build a user-level prompt that combines the financial snapshot with the user's question.
    
    Args:
        question: The user's natural language question
        snapshot: Dictionary containing the user's financial summary from /analyze
        
    Returns:
        Formatted user prompt string
    """
    summary = snapshot.get('summary', {})
    flags = snapshot.get('flags', [])
    
    # Format the snapshot into a readable summary
    snapshot_text = "Here's my current financial snapshot:\n\n"
    
    # Add summary numbers
    snapshot_text += f"📊 Income: ₹{summary.get('total_income', 0):,.2f}\n"
    snapshot_text += f"📊 Total Expenses: ₹{summary.get('total_expenses', 0):,.2f}\n"
    snapshot_text += f"   - Needs: ₹{summary.get('total_needs', 0):,.2f}\n"
    snapshot_text += f"   - Wants: ₹{summary.get('total_wants', 0):,.2f}\n"
    snapshot_text += f"📊 Savings Potential: ₹{summary.get('savings_potential', 0):,.2f}\n"
    snapshot_text += f"📊 Suggested Weekly Budget: ₹{summary.get('suggested_weekly_budget', 0):,.2f}\n"
    
    # Add top insights/flags
    if flags:
        snapshot_text += "\n🎯 Key Insights:\n"
        for flag in flags[:3]:  # Show top 3 flags
            snapshot_text += f"   - {flag}\n"
    
    # Add the user's question
    snapshot_text += f"\n❓ My Question: {question}"
    
    return snapshot_text
