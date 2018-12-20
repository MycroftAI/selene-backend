import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AppService } from './app.service';
import { GlobalnavModule } from 'globalnav';
import { PageNotFoundModule } from 'page-not-found';
import { MaterialModule } from './shared/material.module';
import { SkillsModule } from './skills/skills.module';
import { PageNotFoundComponent } from './page-not-found/page-not-found.component';

@NgModule(
    {
        declarations: [ AppComponent, PageNotFoundComponent ],
        imports: [
            BrowserModule,
            BrowserAnimationsModule,
            GlobalnavModule,
            HttpClientModule,
            MaterialModule,
            PageNotFoundModule,
            SkillsModule,
            AppRoutingModule
        ],
        providers: [ AppService ],
        bootstrap: [ AppComponent ]
    }
)
export class AppModule { }
