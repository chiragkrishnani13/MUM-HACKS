import { Component, OnInit } from '@angular/core';
import { DataService } from '../../services/data.service';
import { AnalysisResponse } from '../../services/api.service';

@Component({
  selector: 'app-spending',
  templateUrl: './spending.component.html',
  styleUrls: ['./spending.component.css']
})
export class SpendingComponent implements OnInit {
  analysis: AnalysisResponse | null = null;

  constructor(private dataService: DataService) {}

  ngOnInit(): void {
    this.dataService.analysis$.subscribe(data => {
      this.analysis = data;
    });
  }
}
