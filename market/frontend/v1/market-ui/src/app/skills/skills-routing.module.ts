import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { SkillsComponent } from "./skills.component";
import { SkillDetailComponent } from "./skill-detail/skill-detail.component";

const routes: Routes = [
    { path: 'skills', component: SkillsComponent },
    { path: 'skill/:id', component: SkillDetailComponent}
];

@NgModule({
  imports: [ RouterModule.forChild(routes) ],
  exports: [ RouterModule ]
})
export class SkillsRoutingModule { }
