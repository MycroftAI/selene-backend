import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FlexLayoutModule } from "@angular/flex-layout";

import { FontAwesomeModule } from "@fortawesome/angular-fontawesome";

import { MaterialModule } from "../shared/material.module";
import { HeaderComponent } from './header.component';
import { LoginComponent } from "./login/login.component";

@NgModule({
    imports: [
        CommonModule,
        FlexLayoutModule,
        FontAwesomeModule,
        MaterialModule
    ],
    declarations: [ HeaderComponent, LoginComponent ],
    exports: [ HeaderComponent ],
})
export class HeaderModule { }
