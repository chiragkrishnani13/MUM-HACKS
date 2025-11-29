import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { OverviewComponent } from './pages/overview/overview.component';
import { ChatComponent } from './pages/chat/chat.component';
import { GoalsComponent } from './pages/goals/goals.component';
import { SpendingComponent } from './pages/spending/spending.component';
import { ActionPlanComponent } from './pages/action-plan/action-plan.component';
import { InsightsComponent } from './pages/insights/insights.component';
import { ChallengesComponent } from './pages/challenges/challenges.component';

const routes: Routes = [
  { path: '', redirectTo: '/overview', pathMatch: 'full' },
  { path: 'overview', component: OverviewComponent },
  { path: 'chat', component: ChatComponent },
  { path: 'goals', component: GoalsComponent },
  { path: 'spending', component: SpendingComponent },
  { path: 'insights', component: InsightsComponent },
  { path: 'challenges', component: ChallengesComponent },
  { path: 'action-plan', component: ActionPlanComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
