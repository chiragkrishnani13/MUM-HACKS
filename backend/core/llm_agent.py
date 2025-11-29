"""
LLM-powered financial coach agent.
"""

import os
from typing import Dict, Any
from openai import OpenAI
from utils.prompt_templates import get_coach_system_prompt, build_user_prompt


# Initialize OpenRouter client (OpenAI-compatible API)
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY", ""),
    base_url="https://openrouter.ai/api/v1"
)


def ask_coach(question: str, user_snapshot: dict) -> str:
    """
    Call the LLM API to get financial coaching advice.
    
    The model:
    - Uses a system prompt that defines the coach persona
    - Receives the user's financial snapshot and question
    - Provides practical, empathetic, actionable advice
    - References actual numbers from the user's data
    
    Args:
        question: User's natural language question
        user_snapshot: Dictionary with financial summary from /analyze endpoint
        
    Returns:
        AI coach's response as a string
    """
    try:
        # Build the prompts
        system_prompt = get_coach_system_prompt()
        user_prompt = build_user_prompt(question, user_snapshot)
        
        print(f"Calling OpenRouter API with model: anthropic/claude-3.5-sonnet")
        
        # Call OpenRouter API with Claude Sonnet for better conversational responses
        response = client.chat.completions.create(
            model="anthropic/claude-3.5-sonnet",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.9,
            max_tokens=1000,
            top_p=0.95,
            extra_headers={
                "HTTP-Referer": "https://flexicoach.app",
                "X-Title": "FlexiCoach"
            }
        )
        
        # Extract the response
        answer = response.choices[0].message.content.strip()
        print(f"OpenRouter API success, response length: {len(answer)}")
        return answer
        
    except Exception as e:
        # Fallback response if API fails
        print(f"LLM API error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return (
            "I'm having trouble connecting to the AI coach right now. "
            "Here's a basic rule of thumb: Try to keep your 'wants' spending below 30% of your income, "
            "prioritize building an emergency fund covering at least 3 months of expenses, "
            "and review your spending weekly to stay on track. "
            "For irregular gig income, try to save during high-earning periods to buffer low-earning months."
        )
