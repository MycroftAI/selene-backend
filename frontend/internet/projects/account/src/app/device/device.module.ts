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

import { AttributeComponent } from './attribute/attribute.component';
import { DeviceComponent } from './device.component';
import { DeviceService } from './device.service';
import { GroupComponent } from './group/group.component';
import { PlacementComponent } from './placement/placement.component';
import { RemoveComponent } from './remove/remove.component';

@NgModule({
    declarations: [
        AttributeComponent,
        DeviceComponent,
        GroupComponent,
        PlacementComponent,
        RemoveComponent
    ],
    entryComponents: [
        GroupComponent,
        PlacementComponent,
        RemoveComponent
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
