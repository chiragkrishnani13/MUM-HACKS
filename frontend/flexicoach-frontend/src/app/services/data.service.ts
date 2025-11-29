import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { AnalysisResponse } from './api.service';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private analysisSubject = new BehaviorSubject<AnalysisResponse | null>(null);
  public analysis$: Observable<AnalysisResponse | null> = this.analysisSubject.asObservable();

  setAnalysis(data: AnalysisResponse): void {
    this.analysisSubject.next(data);
  }

  getAnalysis(): AnalysisResponse | null {
    return this.analysisSubject.value;
  }
}
