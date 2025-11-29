"""
Challenge Management Module
Handles user challenge tracking, status updates, and persistence.
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel


class ChallengeStatus:
    """Challenge status constants"""
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    COMPLETED = "completed"


class UserChallenge(BaseModel):
    """Model for user's challenge state"""
    userId: str
    challengeId: str
    status: str
    current: float = 0.0
    target: float
    startedAt: Optional[str] = None
    completedAt: Optional[str] = None
    title: str
    description: str
    difficulty: str
    reward: str
    points: int


class ChallengeManager:
    """
    Manages user challenges in memory.
    In production, this would use a database (PostgreSQL, MongoDB, etc.)
    """
    
    def __init__(self):
        # In-memory storage: {userId: {challengeId: UserChallenge}}
        self._user_challenges: Dict[str, Dict[str, UserChallenge]] = {}
    
    def start_challenge(
        self, 
        user_id: str, 
        challenge_id: str,
        challenge_data: Dict
    ) -> UserChallenge:
        """
        Start a new challenge for a user.
        
        Args:
            user_id: User identifier
            challenge_id: Challenge identifier
            challenge_data: Challenge metadata (title, description, etc.)
            
        Returns:
            UserChallenge object with updated status
        """
        if user_id not in self._user_challenges:
            self._user_challenges[user_id] = {}
        
        # Check if challenge already exists
        if challenge_id in self._user_challenges[user_id]:
            existing = self._user_challenges[user_id][challenge_id]
            if existing.status == ChallengeStatus.ACTIVE:
                raise ValueError("Challenge is already active")
            if existing.status == ChallengeStatus.COMPLETED:
                raise ValueError("Challenge is already completed")
        
        # Create new user challenge
        user_challenge = UserChallenge(
            userId=user_id,
            challengeId=challenge_id,
            status=ChallengeStatus.ACTIVE,
            current=0.0,
            target=challenge_data.get('target', 0),
            startedAt=datetime.utcnow().isoformat(),
            title=challenge_data.get('title', ''),
            description=challenge_data.get('description', ''),
            difficulty=challenge_data.get('difficulty', 'Medium'),
            reward=challenge_data.get('reward', ''),
            points=challenge_data.get('points', 0)
        )
        
        self._user_challenges[user_id][challenge_id] = user_challenge
        
        return user_challenge
    
    def get_user_challenges(self, user_id: str) -> Dict[str, List[UserChallenge]]:
        """
        Get all challenges for a user, organized by status.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with 'activeChallenges' and 'completedChallenges' lists
        """
        if user_id not in self._user_challenges:
            return {
                "activeChallenges": [],
                "completedChallenges": []
            }
        
        user_challenges = self._user_challenges[user_id].values()
        
        active = [c for c in user_challenges if c.status == ChallengeStatus.ACTIVE]
        completed = [c for c in user_challenges if c.status == ChallengeStatus.COMPLETED]
        
        return {
            "activeChallenges": active,
            "completedChallenges": completed
        }
    
    def update_challenge_progress(
        self, 
        user_id: str, 
        challenge_id: str, 
        current_value: float
    ) -> UserChallenge:
        """
        Update the progress of a challenge.
        
        Args:
            user_id: User identifier
            challenge_id: Challenge identifier
            current_value: New current progress value
            
        Returns:
            Updated UserChallenge object
        """
        if user_id not in self._user_challenges:
            raise ValueError("User has no challenges")
        
        if challenge_id not in self._user_challenges[user_id]:
            raise ValueError("Challenge not found for user")
        
        user_challenge = self._user_challenges[user_id][challenge_id]
        
        if user_challenge.status != ChallengeStatus.ACTIVE:
            raise ValueError("Can only update active challenges")
        
        user_challenge.current = current_value
        
        # Auto-complete if target reached
        if current_value >= user_challenge.target:
            user_challenge.status = ChallengeStatus.COMPLETED
            user_challenge.completedAt = datetime.utcnow().isoformat()
        
        return user_challenge
    
    def get_challenge(self, user_id: str, challenge_id: str) -> Optional[UserChallenge]:
        """Get a specific challenge for a user"""
        if user_id in self._user_challenges:
            return self._user_challenges[user_id].get(challenge_id)
        return None
    
    def delete_challenge(self, user_id: str, challenge_id: str) -> bool:
        """Delete a challenge (for admin/testing purposes)"""
        if user_id in self._user_challenges and challenge_id in self._user_challenges[user_id]:
            del self._user_challenges[user_id][challenge_id]
            return True
        return False


# Singleton instance
challenge_manager = ChallengeManager()
