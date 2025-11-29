import { Component, OnInit } from '@angular/core';
import { DataService } from '../../services/data.service';
import { AnalysisResponse } from '../../services/api.service';

@Component({
  selector: 'app-action-plan',
  templateUrl: './action-plan.component.html',
  styleUrls: ['./action-plan.component.css']
})
export class ActionPlanComponent implements OnInit {
  analysis: AnalysisResponse | null = null;

  constructor(private dataService: DataService) {}

  ngOnInit(): void {
    this.dataService.analysis$.subscribe(data => {
      this.analysis = data;
    });
  }
}
