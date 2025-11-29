"""
FlexiCoach FastAPI Backend - AI-powered money coach for gig workers and young professionals.
"""

import io
import logging
from typing import Dict, Any

import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from core.data_cleaning import clean_transactions
from core.spending_classifier import classify_spending
from core.budget_planner import generate_budget_plan
from core.llm_agent import ask_coach
from core.advanced_features import (
    detect_spending_patterns,
    predict_next_month,
    compare_to_benchmarks,
    generate_savings_goals,
    financial_health_score
)
from core.dynamic_features import (
    calculate_financial_momentum,
    detect_spending_triggers,
    generate_smart_challenges,
    calculate_financial_personality,
    generate_peer_comparison,
    calculate_money_habits_score
)
from core.challenge_manager import challenge_manager, UserChallenge


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize FastAPI app
app = FastAPI(
    title="FlexiCoach API",
    description="AI-powered financial coaching for gig workers and young professionals",
    version="1.0.0"
)


# Enable CORS for all origins (hackathon/demo setting)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    question: str
    user_snapshot: Dict[str, Any]


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str


class StartChallengeRequest(BaseModel):
    """Request model for starting a challenge."""
    userId: str
    challengeId: str
    challengeData: Dict[str, Any]


class StartChallengeResponse(BaseModel):
    """Response model for starting a challenge."""
    success: bool
    message: str
    challenge: UserChallenge


class UserChallengesResponse(BaseModel):
    """Response model for user challenges."""
    activeChallenges: list
    completedChallenges: list


class UpdateProgressRequest(BaseModel):
    """Request model for updating challenge progress."""
    currentValue: float


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "FlexiCoach API",
        "version": "1.0.0"
    }


@app.post("/analyze")
async def analyze_transactions(file: UploadFile = File(...)):
    """
    Analyze uploaded transaction CSV and return financial insights.
    
    Process:
    1. Read and validate CSV file
    2. Clean and normalize transaction data
    3. Classify transactions (needs vs wants, categories)
    4. Generate budget plan with insights
    
    Args:
        file: Uploaded CSV file with transaction data
        
    Returns:
        JSON with summary, categories, weekly_series, and flags
    """
    try:
        logger.info(f"Received file: {file.filename}")
        
        # Read CSV into DataFrame
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        logger.info(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")
        logger.info(f"Column names: {list(df.columns)}")
        logger.info(f"First few rows:\n{df.head()}")
        
        # Process the data through the pipeline
        df_clean = clean_transactions(df)
        logger.info(f"Data cleaned: {len(df_clean)} valid transactions")
        
        df_labeled = classify_spending(df_clean)
        logger.info("Transactions classified")
        
        plan = generate_budget_plan(df_labeled)
        logger.info("Budget plan generated")
        
        # Add advanced features
        plan['patterns'] = detect_spending_patterns(df_labeled)
        plan['predictions'] = predict_next_month(df_labeled)
        plan['benchmarks'] = compare_to_benchmarks(df_labeled)
        plan['savings_goals'] = generate_savings_goals(df_labeled)
        plan['health_score'] = financial_health_score(df_labeled)
        
        # Add dynamic features
        plan['momentum'] = calculate_financial_momentum(df_labeled)
        plan['spending_triggers'] = detect_spending_triggers(df_labeled)
        plan['challenges'] = generate_smart_challenges(df_labeled)
        plan['personality'] = calculate_financial_personality(df_labeled)
        plan['peer_comparison'] = generate_peer_comparison(df_labeled)
        plan['habits_score'] = calculate_money_habits_score(df_labeled)
        
        return plan
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process transactions: {str(e)}"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat_with_coach(req: ChatRequest):
    """
    Chat with the AI financial coach.
    
    Process:
    1. Receive user's question and financial snapshot
    2. Call LLM with structured prompt
    3. Return personalized financial advice
    
    Args:
        req: ChatRequest with question and user_snapshot
        
    Returns:
        JSON with AI coach's answer
    """
    try:
        logger.info(f"Chat request: {req.question[:50]}...")
        
        # Get response from LLM agent
        answer = ask_coach(req.question, req.user_snapshot)
        
        logger.info("Chat response generated")
        
        return ChatResponse(answer=answer)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        # Return a friendly fallback instead of failing
        return ChatResponse(
            answer=(
                "I'm having a bit of trouble right now, but here's some general advice: "
                "Focus on tracking your expenses consistently, try to save at least 20% of your income, "
                "and build an emergency fund covering 3-6 months of expenses. "
                "If you have irregular income from gig work, save more during high-earning periods. "
                "Let me know if you'd like to try your question again!"
            )
        )


@app.post("/compare")
async def compare_periods(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    """
    Compare two different time periods of transactions.
    
    Useful for:
    - Month-to-month comparison
    - Before/after behavior change
    - Year-over-year analysis
    """
    try:
        # Process first file
        contents1 = await file1.read()
        df1 = pd.read_csv(io.BytesIO(contents1))
        df1_clean = clean_transactions(df1)
        df1_labeled = classify_spending(df1_clean)
        
        # Process second file
        contents2 = await file2.read()
        df2 = pd.read_csv(io.BytesIO(contents2))
        df2_clean = clean_transactions(df2)
        df2_labeled = classify_spending(df2_clean)
        
        # Compare summaries
        summary1 = {
            "income": df1_labeled[~df1_labeled['is_expense']]['amount'].sum(),
            "expenses": df1_labeled[df1_labeled['is_expense']]['amount'].sum(),
            "needs": df1_labeled[df1_labeled['need_vs_want'] == 'need']['amount'].sum(),
            "wants": df1_labeled[df1_labeled['need_vs_want'] == 'want']['amount'].sum(),
        }
        
        summary2 = {
            "income": df2_labeled[~df2_labeled['is_expense']]['amount'].sum(),
            "expenses": df2_labeled[df2_labeled['is_expense']]['amount'].sum(),
            "needs": df2_labeled[df2_labeled['need_vs_want'] == 'need']['amount'].sum(),
            "wants": df2_labeled[df2_labeled['need_vs_want'] == 'want']['amount'].sum(),
        }
        
        changes = {
            "income_change": round(summary2["income"] - summary1["income"], 2),
            "expenses_change": round(summary2["expenses"] - summary1["expenses"], 2),
            "needs_change": round(summary2["needs"] - summary1["needs"], 2),
            "wants_change": round(summary2["wants"] - summary1["wants"], 2),
            "income_percent": round(((summary2["income"] - summary1["income"]) / summary1["income"] * 100) if summary1["income"] > 0 else 0, 1),
            "expenses_percent": round(((summary2["expenses"] - summary1["expenses"]) / summary1["expenses"] * 100) if summary1["expenses"] > 0 else 0, 1),
        }
        
        return {
            "period1": summary1,
            "period2": summary2,
            "changes": changes,
            "message": "Comparison complete"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/export/{format}")
async def export_data(format: str):
    """
    Export user data in different formats (future: PDF report, CSV summary).
    """
    if format not in ["json", "pdf"]:
        raise HTTPException(status_code=400, detail="Supported formats: json, pdf")
    
    return {
        "message": f"Export in {format} format",
        "status": "Feature coming soon"
    }


# ==================== Challenge Management Endpoints ====================

@app.post("/challenges/start", response_model=StartChallengeResponse)
async def start_challenge(req: StartChallengeRequest):
    """
    Start a new challenge for a user.
    
    Args:
        req: StartChallengeRequest with userId, challengeId, and challengeData
        
    Returns:
        StartChallengeResponse with success status and challenge details
    """
    try:
        logger.info(f"Starting challenge {req.challengeId} for user {req.userId}")
        
        user_challenge = challenge_manager.start_challenge(
            user_id=req.userId,
            challenge_id=req.challengeId,
            challenge_data=req.challengeData
        )
        
        logger.info(f"Challenge {req.challengeId} started successfully")
        
        return StartChallengeResponse(
            success=True,
            message="Challenge started successfully",
            challenge=user_challenge
        )
        
    except ValueError as e:
        logger.error(f"Validation error starting challenge: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error starting challenge: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start challenge: {str(e)}")


@app.get("/challenges/user/{userId}", response_model=UserChallengesResponse)
async def get_user_challenges(userId: str):
    """
    Get all challenges for a specific user.
    
    Args:
        userId: User identifier
        
    Returns:
        UserChallengesResponse with activeChallenges and completedChallenges lists
    """
    try:
        logger.info(f"Fetching challenges for user {userId}")
        
        challenges = challenge_manager.get_user_challenges(userId)
        
        logger.info(f"Found {len(challenges['activeChallenges'])} active and {len(challenges['completedChallenges'])} completed challenges")
        
        return UserChallengesResponse(**challenges)
        
    except Exception as e:
        logger.error(f"Error fetching user challenges: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch challenges: {str(e)}")


@app.patch("/challenges/progress/{userId}/{challengeId}")
async def update_challenge_progress(userId: str, challengeId: str, req: UpdateProgressRequest):
    """
    Update the progress of a specific challenge.
    
    Args:
        userId: User identifier
        challengeId: Challenge identifier
        req: UpdateProgressRequest with currentValue
        
    Returns:
        Updated UserChallenge object
    """
    try:
        logger.info(f"Updating challenge {challengeId} progress for user {userId} to {req.currentValue}")
        
        user_challenge = challenge_manager.update_challenge_progress(
            user_id=userId,
            challenge_id=challengeId,
            current_value=req.currentValue
        )
        
        logger.info(f"Challenge progress updated. Status: {user_challenge.status}")
        
        return user_challenge
        
    except ValueError as e:
        logger.error(f"Validation error updating challenge: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error updating challenge progress: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update challenge: {str(e)}")


@app.delete("/challenges/{userId}/{challengeId}")
async def delete_challenge(userId: str, challengeId: str):
    """
    Delete a challenge (admin/testing purposes).
    
    Args:
        userId: User identifier
        challengeId: Challenge identifier
        
    Returns:
        Success message
    """
    try:
        success = challenge_manager.delete_challenge(userId, challengeId)
        
        if not success:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        return {"message": "Challenge deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting challenge: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete challenge: {str(e)}")


# Optional: Run with uvicorn programmatically
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
