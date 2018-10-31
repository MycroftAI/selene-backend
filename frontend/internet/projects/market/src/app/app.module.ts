import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HeaderModule } from './header/header.module';
import { MaterialModule } from './shared/material.module';
import { LoginService } from './shared/login.service';
import { SkillsModule } from './skills/skills.module';
import { PageNotFoundComponent } from './page-not-found/page-not-found.component';

@NgModule(
    {
        declarations: [ AppComponent, PageNotFoundComponent ],
        imports: [
            BrowserModule,
            BrowserAnimationsModule,
            HttpClientModule,
            HeaderModule,
            MaterialModule,
            SkillsModule,
            AppRoutingModule
        ],
        providers: [ LoginService ],
        bootstrap: [ AppComponent ]
    }
)
export class AppModule { }
