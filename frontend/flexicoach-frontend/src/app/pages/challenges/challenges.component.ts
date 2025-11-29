import { Component, OnInit } from '@angular/core';
import { DataService } from '../../services/data.service';
import { AnalysisResponse, ApiService, Challenge, ChallengeStatus } from '../../services/api.service';

@Component({
  selector: 'app-challenges',
  templateUrl: './challenges.component.html',
  styleUrls: ['./challenges.component.css']
})
export class ChallengesComponent implements OnInit {
  analysis: AnalysisResponse | null = null;
  userId: string = 'default_user'; // In production, get from auth service
  challengeStates: Map<string, { loading: boolean; error: string | null }> = new Map();

  constructor(
    private dataService: DataService,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.dataService.analysis$.subscribe(data => {
      this.analysis = data;
      if (data && data.challenges) {
        // Initialize challenge states and status field
        data.challenges.forEach(challenge => {
          // Ensure status field exists (backend doesn't provide it initially)
          if (!challenge.status) {
            challenge.status = 'not_started';
          }
          this.challengeStates.set(challenge.id, { loading: false, error: null });
        });
        // Fetch user's active challenges to sync status
        this.syncChallengeStatuses();
      }
    });
  }

  /**
   * Sync challenge statuses with backend data
   */
  private syncChallengeStatuses(): void {
    this.apiService.getUserChallenges(this.userId).subscribe({
      next: (response) => {
        if (this.analysis && this.analysis.challenges) {
          // Update statuses for active challenges
          response.activeChallenges.forEach(activeChallenge => {
            const challenge = this.analysis!.challenges!.find(c => c.id === activeChallenge.id);
            if (challenge) {
              challenge.status = 'active';
              challenge.current = activeChallenge.current;
              challenge.startedAt = activeChallenge.startedAt;
            }
          });
          
          // Update statuses for completed challenges
          response.completedChallenges.forEach(completedChallenge => {
            const challenge = this.analysis!.challenges!.find(c => c.id === completedChallenge.id);
            if (challenge) {
              challenge.status = 'completed';
              challenge.current = completedChallenge.current;
              challenge.completedAt = completedChallenge.completedAt;
            }
          });
        }
      },
      error: (err) => {
        console.error('Error syncing challenge statuses:', err);
        // Fail silently - user can still interact with challenges
      }
    });
  }

  /**
   * Accept/Start a challenge
   */
  acceptChallenge(challenge: Challenge): void {
    console.log('acceptChallenge called for:', challenge.id, challenge);
    
    if (challenge.status === 'active' || challenge.status === 'completed') {
      console.log('Challenge already started/completed');
      return; // Already started or completed
    }

    const state = this.challengeStates.get(challenge.id);
    if (!state || state.loading) {
      console.log('Challenge already processing or no state');
      return; // Already processing
    }

    // Set loading state
    this.challengeStates.set(challenge.id, { loading: true, error: null });
    console.log('Starting challenge API call...');

    this.apiService.startChallenge(this.userId, challenge.id, challenge).subscribe({
      next: (response) => {
        if (response.success) {
          // Update local challenge state
          challenge.status = 'active';
          challenge.current = 0;
          challenge.startedAt = new Date().toISOString();
          
          // Update state
          this.challengeStates.set(challenge.id, { loading: false, error: null });
          
          console.log(`Challenge "${challenge.title}" started successfully`);
        } else {
          // Handle failure
          this.challengeStates.set(challenge.id, { 
            loading: false, 
            error: response.message || 'Failed to start challenge' 
          });
        }
      },
      error: (err) => {
        console.error('Error starting challenge:', err);
        this.challengeStates.set(challenge.id, { 
          loading: false, 
          error: 'Failed to start challenge. Please try again.' 
        });
      }
    });
  }

  /**
   * Get button label based on challenge status
   */
  getButtonLabel(challenge: Challenge): string {
    const state = this.challengeStates.get(challenge.id);
    
    if (state?.loading) {
      return 'Starting...';
    }
    
    switch (challenge.status) {
      case 'active':
        return 'In Progress';
      case 'completed':
        return 'Completed ✓';
      case 'not_started':
      default:
        return 'Accept Challenge';
    }
  }

  /**
   * Check if button should be disabled
   */
  isButtonDisabled(challenge: Challenge): boolean {
    const state = this.challengeStates.get(challenge.id);
    return state?.loading || challenge.status === 'active' || challenge.status === 'completed';
  }

  /**
   * Get button CSS class based on status
   */
  getButtonClass(challenge: Challenge): string {
    switch (challenge.status) {
      case 'active':
        return 'accept-btn in-progress';
      case 'completed':
        return 'accept-btn completed';
      case 'not_started':
      default:
        return 'accept-btn';
    }
  }

  getDifficultyClass(difficulty: string): string {
    return difficulty.toLowerCase();
  }

  getProgressPercentage(challenge: Challenge): number {
    if (!challenge.target || challenge.target === 0) return 0;
    const current = challenge.current || 0;
    return Math.min(100, (current / challenge.target) * 100);
  }
}
