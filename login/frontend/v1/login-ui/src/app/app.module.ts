import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { FlexModule } from "@angular/flex-layout";
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { AuthModule } from "./auth/auth.module";
import { CoreModule } from "./core/core.module";

@NgModule({
    declarations: [ AppComponent ],
    imports: [
        BrowserModule,
        AuthModule,
        BrowserAnimationsModule,
        CoreModule.forRoot(),
        FlexModule,
    ],
    providers: [ ],
    bootstrap: [ AppComponent ]
})
export class AppModule { }
