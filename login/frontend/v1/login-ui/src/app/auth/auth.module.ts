import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from "@angular/forms";
import { FlexModule } from "@angular/flex-layout";
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

import { AuthComponent } from './auth.component';
import { AuthService } from "./auth.service";

@NgModule({
    declarations: [ AuthComponent ],
    exports: [ AuthComponent ],
    imports: [
        CommonModule,
        FlexModule,
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
    providers: [ AuthService ]
})
export class AuthModule { }
