import {Component, Input, OnInit} from '@angular/core';
import { MatDialogRef } from '@angular/material';

import { faTrashAlt } from '@fortawesome/free-solid-svg-icons';

import { DeviceAttribute } from '../device.service';
import { GeographyEditComponent } from './geography/geography-edit.component';
import { GroupEditComponent } from './group/group-edit.component';
import { PlacementEditComponent } from './placement/placement-edit.component';


@Component({
  selector: 'account-device-attribute-edit',
  templateUrl: './attr-edit.component.html',
  styleUrls: ['./attr-edit.component.scss']
})
export class AttrEditComponent implements OnInit {
    @Input() dialogData: string;
    @Input() dialogInstructions: string;
    @Input() dialogRef: MatDialogRef<GeographyEditComponent | GroupEditComponent | PlacementEditComponent>;
    @Input() dialogTitle: string;
    @Input() possibleValues: DeviceAttribute[];
    public deleteIcon = faTrashAlt;

    constructor() {
    }

    ngOnInit() {
    }

    onCancelClick(): void {
        this.dialogRef.close();
    }
}
