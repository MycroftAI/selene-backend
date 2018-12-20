import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FlexLayoutModule } from '@angular/flex-layout';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { BackgroundModule } from './background/background.module';
import { LoginModule } from './login/login.module';
import { LogoutModule } from './logout/logout.module';
import { PageNotFoundModule } from 'page-not-found';

@NgModule({
    declarations: [ AppComponent ],
    imports: [
        BrowserModule,
        BackgroundModule,
        BrowserAnimationsModule,
        FlexLayoutModule,
        LoginModule,
        LogoutModule,
        PageNotFoundModule,
        AppRoutingModule
    ],
    providers: [ ],
    bootstrap: [ AppComponent ]
})
export class AppModule { }
