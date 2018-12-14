import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FlexLayoutModule } from '@angular/flex-layout';
import { LeafletModule } from '@asymmetrik/ngx-leaflet';

import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
    MatButtonModule,
    MatButtonToggleModule,
    MatCardModule,
    MatDividerModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatSlideToggleModule,
    MatToolbarModule
} from '@angular/material';

import { ProfileComponent } from './profile.component';
import { LoginComponent } from './login/login.component';
import { PersonalComponent } from './personal/personal.component';
import { SubscriptionComponent } from './subscription/subscription.component';
import { DeleteComponent } from './delete/delete.component';
import { AgreementsComponent } from './agreements/agreements.component';

@NgModule({
    declarations: [
        ProfileComponent,
        LoginComponent,
        PersonalComponent,
        SubscriptionComponent,
        DeleteComponent,
        AgreementsComponent
    ],
    entryComponents: [
        LoginComponent
    ],
    imports: [
        CommonModule,
        FlexLayoutModule,
        FontAwesomeModule,
        LeafletModule,
        MatButtonModule,
        MatButtonToggleModule,
        MatCardModule,
        MatDividerModule,
        MatExpansionModule,
        MatFormFieldModule,
        MatInputModule,
        MatSelectModule,
        MatSlideToggleModule,
        MatToolbarModule
    ]
})
export class ProfileModule { }
