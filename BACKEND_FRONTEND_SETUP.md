# FlexiCoach - Backend & Frontend Connection Guide

## 🚀 Quick Start

### 1️⃣ Start the Backend Server

```powershell
# Navigate to backend directory
cd c:\Users\sidha\MUM-HACKS\backend

# Install dependencies (first time only)
pip install -r requirements.txt

# Make sure your .env file has the OpenRouter API key
# .env should contain:
# OPENROUTER_API_KEY=your-actual-key-here

# Start the FastAPI server
python main.py
```

✅ Backend will be running at: **http://localhost:8000**

Test it by visiting: http://localhost:8000 in your browser

---

### 2️⃣ Start the Angular Frontend

```powershell
# Open a NEW terminal window
# Navigate to frontend directory
cd c:\Users\sidha\MUM-HACKS\frontend\flexicoach-frontend

# Install dependencies (first time only)
npm install

# Start the Angular dev server with proxy
ng serve --proxy-config proxy.conf.json
```

✅ Frontend will be running at: **http://localhost:4200**

---

## 📡 API Endpoints Available

### GET /
Health check endpoint
- **URL:** `http://localhost:8000/`
- **Response:** `{ "status": "healthy", "service": "FlexiCoach API", "version": "1.0.0" }`

### POST /analyze
Upload CSV file and get financial analysis
- **URL:** `http://localhost:8000/analyze`
- **Method:** POST
- **Content-Type:** `multipart/form-data`
- **Body:** Form data with `file` field containing CSV
- **Response:**
```json
{
  "summary": {
    "total_income": 50000.0,
    "total_expenses": 35000.0,
    "total_needs": 25000.0,
    "total_wants": 10000.0,
    "savings_potential": 15000.0,
    "suggested_weekly_budget": 8750.0
  },
  "categories": [
    { "name": "food", "amount": 12000.0 },
    { "name": "transport", "amount": 5000.0 }
  ],
  "weekly_series": [
    { "week_start": "2025-11-01", "total_spent": 8500.0 }
  ],
  "flags": [
    "✅ Great! You have ₹15000.0 savings potential (30.0% of income)."
  ]
}
```

### POST /chat
Chat with AI financial coach
- **URL:** `http://localhost:8000/chat`
- **Method:** POST
- **Content-Type:** `application/json`
- **Body:**
```json
{
  "question": "How can I save more money?",
  "user_snapshot": {
    "summary": { "total_income": 50000, "total_expenses": 35000, ... },
    "categories": [...],
    "flags": [...]
  }
}
```
- **Response:**
```json
{
  "answer": "Based on your snapshot, here are some tips..."
}
```

---

## 🔧 Angular Service Integration

### Create API Service

Create `src/app/services/api.service.ts`:

```typescript
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

export interface AnalysisResponse {
  summary: Summary;
  categories: Category[];
  weekly_series: WeeklySeries[];
  flags: string[];
}

export interface ChatRequest {
  question: string;
  user_snapshot: AnalysisResponse;
}

export interface ChatResponse {
  answer: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  // Using proxy configuration - requests to /api will be forwarded to http://localhost:8000
  private baseUrl = '/api';

  constructor(private http: HttpClient) {}

  /**
   * Upload CSV file for analysis
   */
  analyzeTransactions(file: File): Observable<AnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.http.post<AnalysisResponse>(`${this.baseUrl}/analyze`, formData);
  }

  /**
   * Chat with AI financial coach
   */
  chatWithCoach(question: string, snapshot: AnalysisResponse): Observable<ChatResponse> {
    const body: ChatRequest = {
      question,
      user_snapshot: snapshot
    };
    
    return this.http.post<ChatResponse>(`${this.baseUrl}/chat`, body);
  }

  /**
   * Health check
   */
  healthCheck(): Observable<any> {
    return this.http.get(`${this.baseUrl}/`);
  }
}
```

### Usage in Component

```typescript
import { Component } from '@angular/core';
import { ApiService, AnalysisResponse } from './services/api.service';

@Component({
  selector: 'app-root',
  template: `
    <input type="file" (change)="onFileSelected($event)" accept=".csv">
    <button (click)="uploadFile()">Analyze Transactions</button>
    
    <div *ngIf="analysis">
      <h2>Total Income: ₹{{ analysis.summary.total_income }}</h2>
      <h2>Total Expenses: ₹{{ analysis.summary.total_expenses }}</h2>
      
      <input [(ngModel)]="question" placeholder="Ask the coach...">
      <button (click)="askCoach()">Ask</button>
      
      <p *ngIf="coachAnswer">{{ coachAnswer }}</p>
    </div>
  `
})
export class AppComponent {
  selectedFile: File | null = null;
  analysis: AnalysisResponse | null = null;
  question = '';
  coachAnswer = '';

  constructor(private apiService: ApiService) {}

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  uploadFile() {
    if (this.selectedFile) {
      this.apiService.analyzeTransactions(this.selectedFile).subscribe({
        next: (response) => {
          this.analysis = response;
          console.log('Analysis:', response);
        },
        error: (err) => console.error('Error:', err)
      });
    }
  }

  askCoach() {
    if (this.analysis && this.question) {
      this.apiService.chatWithCoach(this.question, this.analysis).subscribe({
        next: (response) => {
          this.coachAnswer = response.answer;
        },
        error: (err) => console.error('Error:', err)
      });
    }
  }
}
```

---

## 🧪 Testing the Connection

### Option 1: Using Browser (Manual Test)

1. Start both backend and frontend
2. Open browser DevTools (F12) → Network tab
3. Upload a CSV file in your Angular app
4. Watch the network request to `/api/analyze`
5. Check if you get a 200 OK response with analysis data

### Option 2: Using PowerShell (Backend Only)

Test backend directly:

```powershell
# Test health check
Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get

# Test analyze endpoint (replace with actual CSV path)
$form = @{
    file = Get-Item -Path ".\transactions.csv"
}
Invoke-RestMethod -Uri "http://localhost:8000/analyze" -Method Post -Form $form

# Test chat endpoint
$body = @{
    question = "How can I save more?"
    user_snapshot = @{
        summary = @{
            total_income = 50000
            total_expenses = 35000
            total_needs = 25000
            total_wants = 10000
            savings_potential = 15000
            suggested_weekly_budget = 8750
        }
        categories = @()
        flags = @()
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"
```

---

## ✅ Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 4200
- [ ] `.env` file has `OPENROUTER_API_KEY`
- [ ] `proxy.conf.json` exists in frontend folder
- [ ] Angular HttpClientModule imported in app.module.ts
- [ ] API service created and injected in components
- [ ] CORS enabled in backend (already done)

---

## 🐛 Common Issues

### Issue: CORS Error
**Solution:** Already fixed! Backend has CORS middleware enabled for all origins.

### Issue: 404 Not Found
**Solution:** Make sure:
1. Backend is running
2. Using `/api` prefix in frontend (proxy handles it)
3. Proxy config is being used: `ng serve --proxy-config proxy.conf.json`

### Issue: Connection Refused
**Solution:** Check if backend is running on port 8000

### Issue: OpenRouter API Error
**Solution:** Verify `.env` file has valid `OPENROUTER_API_KEY`

---

## 🎯 Next Steps

1. Create the API service in your Angular app
2. Import `HttpClientModule` in `app.module.ts`
3. Create components for file upload and chat
4. Use the service methods to call backend
5. Display the analysis results with charts (using Chart.js)

Good luck with your hackathon! 🚀
