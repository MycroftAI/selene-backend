import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { GlobalnavModule } from 'globalnav';
import { PageNotFoundModule } from 'page-not-found';
import { DeviceModule } from './device/device.module';
import { ProfileModule } from './profile/profile.module';

@NgModule(
    {
        // declarations: [ AppComponent, PageNotFoundComponent ],
        declarations: [ AppComponent ],
        imports: [
            BrowserModule,
            BrowserAnimationsModule,
            GlobalnavModule,
            HttpClientModule,
            DeviceModule,
            PageNotFoundModule,
            ProfileModule,
            AppRoutingModule
        ],
        providers: [ ],
        bootstrap: [ AppComponent ]
    }
)
export class AppModule { }
