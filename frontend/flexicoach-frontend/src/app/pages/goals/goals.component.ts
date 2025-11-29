import { Component, OnInit } from '@angular/core';
import { DataService } from '../../services/data.service';
import { AnalysisResponse } from '../../services/api.service';

@Component({
  selector: 'app-goals',
  templateUrl: './goals.component.html',
  styleUrls: ['./goals.component.css']
})
export class GoalsComponent implements OnInit {
  analysis: AnalysisResponse | null = null;

  constructor(private dataService: DataService) {}

  ngOnInit(): void {
    this.dataService.analysis$.subscribe(data => {
      this.analysis = data;
    });
  }
}
