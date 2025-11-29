import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService, AnalysisResponse } from './services/api.service';
import { DataService } from './services/data.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'FlexiCoach - AI Money Coach';
  selectedFile: File | null = null;
  analysis: AnalysisResponse | null = null;
  loading = false;
  error = '';
  menuOpen = false;

  constructor(
    private apiService: ApiService,
    private dataService: DataService,
    private router: Router
  ) {
    this.dataService.analysis$.subscribe(data => {
      this.analysis = data;
    });
  }

  toggleMenu(): void {
    this.menuOpen = !this.menuOpen;
  }

  closeMenuOnMobile(): void {
    this.menuOpen = false;
  }

  triggerFileInput(): void {
    document.getElementById('fileInput')?.click();
  }

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0];
    this.error = '';
  }

  analyzeTransactions(): void {
    if (!this.selectedFile) return;

    this.loading = true;
    this.error = '';

    this.apiService.analyzeTransactions(this.selectedFile).subscribe({
      next: (response) => {
        this.dataService.setAnalysis(response);
        this.loading = false;
        this.router.navigate(['/overview']);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to analyze transactions. Please check your CSV format.';
        this.loading = false;
      }
    });
  }
}
