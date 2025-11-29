import { Component, OnInit } from '@angular/core';
import { DataService } from '../../services/data.service';
import { ApiService, AnalysisResponse } from '../../services/api.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit {
  analysis: AnalysisResponse | null = null;
  question = '';
  messages: {type: 'user' | 'coach', text: string}[] = [];
  loading = false;

  constructor(
    private dataService: DataService,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.dataService.analysis$.subscribe(data => {
      this.analysis = data;
    });
  }

  askQuickQuestion(questionText: string): void {
    this.question = questionText;
    this.askCoach();
  }

  getCurrentTime(): string {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  }

  askCoach(): void {
    if (!this.analysis || !this.question.trim()) return;

    const userQuestion = this.question.trim();
    this.messages.push({ type: 'user', text: userQuestion });
    this.question = '';
    this.loading = true;

    this.apiService.chatWithCoach(userQuestion, this.analysis).subscribe({
      next: (response) => {
        this.messages.push({ type: 'coach', text: response.answer });
        this.loading = false;
      },
      error: () => {
        this.messages.push({ 
          type: 'coach', 
          text: 'Sorry, I had trouble processing that. Please try again.' 
        });
        this.loading = false;
      }
    });
  }
}
