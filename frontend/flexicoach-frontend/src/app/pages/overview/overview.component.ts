import { Component, OnInit } from '@angular/core';
import { DataService } from '../../services/data.service';
import { AnalysisResponse } from '../../services/api.service';

@Component({
  selector: 'app-overview',
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.css']
})
export class OverviewComponent implements OnInit {
  analysis: AnalysisResponse | null = null;

  constructor(private dataService: DataService) {}

  ngOnInit(): void {
    this.dataService.analysis$.subscribe(data => {
      this.analysis = data;
    });
  }

  getScoreColor(score: number): string {
    if (score >= 90) return '#3b82f6'; // Blue - Excellent
    if (score >= 70) return '#10b981'; // Green - Good
    if (score >= 40) return '#f59e0b'; // Yellow - Fair
    return '#ef4444'; // Red - Poor
  }

  getScoreEmoji(score: number): string {
    if (score >= 90) return '🏆';
    if (score >= 70) return '👍';
    if (score >= 40) return '🙂';
    return '⚠️';
  }

  getScoreLabel(score: number): string {
    if (score >= 90) return 'Excellent';
    if (score >= 70) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  }
}
