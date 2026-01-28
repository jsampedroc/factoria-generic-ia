import { Routes } from '@angular/router';
import { DashboardComponent } from './dashboard/dashboard.component';
import { OptimizationViewComponent } from './optimization-view/optimization-view.component';
import { HardwareValidationComponent } from './hardware-validation/hardware-validation.component';
import { FinalSummaryComponent } from './final-summary/final-summary.component';
import { SettingsPanelComponent } from './settings-panel/settings-panel.component';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'optimization', component: OptimizationViewComponent },
  { path: 'hardware-validation', component: HardwareValidationComponent },
  { path: 'final-summary', component: FinalSummaryComponent },
  { path: 'settings', component: SettingsPanelComponent },
  { path: '**', redirectTo: '/dashboard' }
];