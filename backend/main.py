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
        
        # Process the data through the pipeline
        df_clean = clean_transactions(df)
        logger.info(f"Data cleaned: {len(df_clean)} valid transactions")
        
        df_labeled = classify_spending(df_clean)
        logger.info("Transactions classified")
        
        plan = generate_budget_plan(df_labeled)
        logger.info("Budget plan generated")
        
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


# Optional: Run with uvicorn programmatically
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
