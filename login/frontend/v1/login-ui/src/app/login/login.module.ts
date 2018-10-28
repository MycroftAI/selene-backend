import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from "@angular/forms";
import { FlexLayoutModule } from "@angular/flex-layout";
import { HttpClientModule } from "@angular/common/http";
import {
    MatButtonModule,
    MatCheckboxModule,
    MatDividerModule,
    MatFormFieldModule,
    MatInputModule,
    MatSnackBarModule
} from "@angular/material";

import { FontAwesomeModule } from "@fortawesome/angular-fontawesome";

import { AntisocialComponent } from './antisocial/antisocial.component';
import { LoginComponent } from './login.component';
import { LoginService } from "./login.service";
import { BackgroundComponent } from '../background/background.component';
import { SocialComponent } from './social/social.component';

@NgModule({
    declarations: [
        AntisocialComponent,
        LoginComponent,
        BackgroundComponent,
        SocialComponent
    ],
    entryComponents: [ LoginComponent ],
    exports: [ LoginComponent ],
    imports: [
        CommonModule,
        FlexLayoutModule,
        FontAwesomeModule,
        FormsModule,
        HttpClientModule,
        MatButtonModule,
        MatCheckboxModule,
        MatDividerModule,
        MatFormFieldModule,
        MatInputModule,
        MatSnackBarModule
    ],
    providers: [ LoginService ]
})
export class LoginModule { }
