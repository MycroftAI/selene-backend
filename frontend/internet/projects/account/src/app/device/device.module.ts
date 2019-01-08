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

import { AttrEditComponent } from './attribute/attr-edit.component';
import { AttrViewComponent } from './attribute/attr-view.component';
import { DeviceComponent } from './device.component';
import { DeviceService } from './device.service';
import { GeographyEditComponent } from './attribute/geography/geography-edit.component';
import { GeographyViewComponent } from './attribute/geography/geography-view.component';
import { GroupEditComponent } from './attribute/group/group-edit.component';
import { GroupViewComponent } from './attribute/group/group-view.component';
import { PlacementEditComponent } from './attribute/placement/placement-edit.component';
import { PlacementViewComponent } from './attribute/placement/placement-view.component';
import { RemoveComponent } from './remove/remove.component';

@NgModule({
    declarations: [
        AttrEditComponent,
        AttrViewComponent,
        DeviceComponent,
        GeographyEditComponent,
        GeographyViewComponent,
        GroupEditComponent,
        GroupViewComponent,
        PlacementEditComponent,
        PlacementViewComponent,
        RemoveComponent
    ],
    entryComponents: [
        GeographyEditComponent,
        GroupEditComponent,
        PlacementEditComponent,
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
