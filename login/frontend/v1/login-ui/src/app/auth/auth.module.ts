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
    MatTabsModule
} from "@angular/material";

import { FontAwesomeModule } from "@fortawesome/angular-fontawesome";

import { AuthComponent } from './auth.component';
import { AuthService } from "./auth.service";
import { AuthSocialComponent } from './auth-social/auth-social.component';
import { AuthAntisocialComponent } from './auth-antisocial/auth-antisocial.component';

@NgModule({
    declarations: [ AuthComponent, AuthSocialComponent, AuthAntisocialComponent ],
    exports: [ AuthComponent ],
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
        MatTabsModule
    ],
    providers: [ AuthService ]
})
export class AuthModule { }
