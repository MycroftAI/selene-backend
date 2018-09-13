import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FlexLayoutModule } from "@angular/flex-layout";
import { FormsModule } from "@angular/forms";

import { AngularFontAwesomeModule } from 'angular-font-awesome';
import { FontAwesomeModule } from "@fortawesome/angular-fontawesome";

import { MaterialModule } from "../shared/material.module";
import { SkillsComponent } from './skills.component'
import { SkillDetailComponent } from "./skill-detail/skill-detail.component";
import { SkillsRoutingModule } from "./skills-routing.module";
import { SkillToolbarComponent } from "./skill-toolbar/skill-toolbar.component";
import { SkillsService } from "./skills.service";
import { SkillSummaryComponent } from "./skill-summary/skill-summary.component";
import { SkillCardHeaderComponent } from './skill-summary/skill-card-header/skill-card-header.component';

@NgModule(
    {
        imports: [
            AngularFontAwesomeModule,
            CommonModule,
            FlexLayoutModule,
            FontAwesomeModule,
            FormsModule,
            MaterialModule,
            SkillsRoutingModule
        ],
        declarations: [
            SkillDetailComponent,
            SkillsComponent,
            SkillToolbarComponent,
            SkillSummaryComponent,
            SkillCardHeaderComponent
        ],
        exports: [ SkillsComponent, SkillDetailComponent ],
        entryComponents: [ SkillDetailComponent ],
        providers: [ SkillsService ]
    }
)
export class SkillsModule { }
