import { Component, OnInit } from '@angular/core';
import { DataService } from '../../services/data.service';
import { AnalysisResponse } from '../../services/api.service';

@Component({
  selector: 'app-insights',
  templateUrl: './insights.component.html',
  styleUrls: ['./insights.component.css']
})
export class InsightsComponent implements OnInit {
  analysis: AnalysisResponse | null = null;

  constructor(private dataService: DataService) {}

  ngOnInit(): void {
    this.dataService.analysis$.subscribe(data => {
      this.analysis = data;
    });
  }

  getMomentumColor(score: number): string {
    if (score >= 70) return '#4caf50';
    if (score >= 55) return '#8bc34a';
    if (score >= 45) return '#ff9800';
    return '#f44336';
  }

  getHabitsArray(): any[] {
    if (!this.analysis?.habits_score?.breakdown) return [];
    const breakdown = this.analysis.habits_score.breakdown;
    return [
      { name: 'Consistency', value: breakdown.consistency },
      { name: 'Mindfulness', value: breakdown.mindfulness },
      { name: 'Planning', value: breakdown.planning },
      { name: 'Impulse Control', value: breakdown.impulse_control },
      { name: 'Savings Discipline', value: breakdown.savings_discipline }
    ];
  }

  getWeakestHabit(): string | null {
    const habits = this.getHabitsArray();
    if (habits.length === 0) return null;
    
    const weakest = habits.reduce((min, habit) => 
      habit.value < min.value ? habit : min
    );
    
    return weakest.name;
  }
}
