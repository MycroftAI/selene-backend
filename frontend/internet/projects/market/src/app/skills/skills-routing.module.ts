import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { SkillSummaryComponent } from './skill-summary/skill-summary.component';
import { SkillDetailComponent } from './skill-detail/skill-detail.component';

const routes: Routes = [
    { path: 'skills', component: SkillSummaryComponent },
    { path: 'skill/:skillName', component: SkillDetailComponent}
];

@NgModule({
  imports: [ RouterModule.forChild(routes) ],
  exports: [ RouterModule ]
})
export class SkillsRoutingModule { }
