import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { OverviewComponent } from './pages/overview/overview.component';
import { ChatComponent } from './pages/chat/chat.component';
import { GoalsComponent } from './pages/goals/goals.component';
import { SpendingComponent } from './pages/spending/spending.component';
import { ActionPlanComponent } from './pages/action-plan/action-plan.component';
import { InsightsComponent } from './pages/insights/insights.component';
import { ChallengesComponent } from './pages/challenges/challenges.component';

@NgModule({
  declarations: [
    AppComponent,
    OverviewComponent,
    ChatComponent,
    GoalsComponent,
    SpendingComponent,
    ActionPlanComponent,
    InsightsComponent,
    ChallengesComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
