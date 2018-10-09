import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { FlexLayoutModule } from "@angular/flex-layout";
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { AuthModule } from "./auth/auth.module";

@NgModule({
    declarations: [ AppComponent ],
    imports: [
        BrowserModule,
        AuthModule,
        BrowserAnimationsModule,
        FlexLayoutModule
    ],
    providers: [ ],
    bootstrap: [ AppComponent ]
})
export class AppModule { }
