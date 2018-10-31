import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FlexLayoutModule } from '@angular/flex-layout';

import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

import { InstallService } from '../skills/install.service';
import { HeaderComponent } from './header.component';
import { MaterialModule } from '../shared/material.module';

@NgModule({
    imports: [
        CommonModule,
        FlexLayoutModule,
        FontAwesomeModule,
        MaterialModule
    ],
    declarations: [ HeaderComponent],
    exports: [ HeaderComponent ],
    providers: [ InstallService ]
})
export class HeaderModule { }
