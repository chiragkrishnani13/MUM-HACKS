import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Summary {
  total_income: number;
  total_expenses: number;
  total_needs: number;
  total_wants: number;
  savings_potential: number;
  suggested_weekly_budget: number;
}

export interface Category {
  name: string;
  amount: number;
}

export interface WeeklySeries {
  week_start: string;
  total_spent: number;
}

export type ChallengeStatus = 'not_started' | 'active' | 'completed';

export interface Challenge {
  id: string;
  title: string;
  description: string;
  difficulty: string;
  target: number;
  current: number;
  reward: string;
  points: number;
  status: ChallengeStatus;
  startedAt?: string;
  completedAt?: string;
}

export interface AnalysisResponse {
  summary: Summary;
  categories: Category[];
  weekly_series: WeeklySeries[];
  flags: string[];
  patterns?: any;
  predictions?: any;
  benchmarks?: any;
  savings_goals?: any[];
  health_score?: any;
  momentum?: any;
  spending_triggers?: any;
  challenges?: Challenge[];
  personality?: any;
  peer_comparison?: any;
  habits_score?: any;
}

export interface ChatRequest {
  question: string;
  user_snapshot: AnalysisResponse;
}

export interface ChatResponse {
  answer: string;
}

export interface StartChallengeRequest {
  userId: string;
  challengeId: string;
  challengeData: {
    title: string;
    description: string;
    difficulty: string;
    target: number;
    reward: string;
    points: number;
  };
}

export interface StartChallengeResponse {
  success: boolean;
  challenge: Challenge;
  message: string;
}

export interface UserChallengesResponse {
  activeChallenges: Challenge[];
  completedChallenges: Challenge[];
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  analyzeTransactions(file: File): Observable<AnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<AnalysisResponse>(`${this.baseUrl}/analyze`, formData);
  }

  chatWithCoach(question: string, snapshot: AnalysisResponse): Observable<ChatResponse> {
    const body: ChatRequest = {
      question,
      user_snapshot: snapshot
    };
    return this.http.post<ChatResponse>(`${this.baseUrl}/chat`, body);
  }

  startChallenge(userId: string, challengeId: string, challengeData: any): Observable<StartChallengeResponse> {
    const body: StartChallengeRequest = {
      userId,
      challengeId,
      challengeData: {
        title: challengeData.title,
        description: challengeData.description,
        difficulty: challengeData.difficulty,
        target: challengeData.target,
        reward: challengeData.reward,
        points: challengeData.points
      }
    };
    console.log('Sending startChallenge request:', body);
    return this.http.post<StartChallengeResponse>(`${this.baseUrl}/challenges/start`, body);
  }

  getUserChallenges(userId: string): Observable<UserChallengesResponse> {
    return this.http.get<UserChallengesResponse>(`${this.baseUrl}/challenges/user/${userId}`);
  }

  updateChallengeProgress(userId: string, challengeId: string, currentValue: number): Observable<Challenge> {
    return this.http.patch<Challenge>(`${this.baseUrl}/challenges/progress`, {
      userId,
      challengeId,
      currentValue
    });
  }
}
