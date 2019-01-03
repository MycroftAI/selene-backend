import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { FlexLayoutModule } from '@angular/flex-layout';
import { FormsModule } from '@angular/forms';
import {
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatDialogModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatInputModule,
    MatRadioModule,
    MatSelectModule,
} from '@angular/material';

import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { DeviceComponent } from './device.component';
import { DeviceGroupComponent } from './device-group/device-group.component';
import { DevicePlacementComponent } from './device-placement/device-placement.component';
import { DeviceService } from './device.service';

@NgModule({
    declarations: [
        DeviceComponent,
        DeviceGroupComponent,
        DevicePlacementComponent
    ],
    entryComponents: [
        DeviceGroupComponent,
        DevicePlacementComponent
    ],
    imports: [
        CommonModule,
        DragDropModule,
        FlexLayoutModule,
        FontAwesomeModule,
        FormsModule,
        MatButtonModule,
        MatCardModule,
        MatCheckboxModule,
        MatDialogModule,
        MatExpansionModule,
        MatFormFieldModule,
        MatInputModule,
        MatRadioModule,
        MatSelectModule,
    ],
    providers: [
        DeviceService
    ]
})
export class DeviceModule { }
