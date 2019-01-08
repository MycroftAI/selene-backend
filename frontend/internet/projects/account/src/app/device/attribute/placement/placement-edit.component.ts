import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';

import { faTrashAlt } from '@fortawesome/free-solid-svg-icons';

import { DevicePlacement, DeviceService} from '../../device.service';


@Component({
  selector: 'account-device-placement',
  templateUrl: './placement-edit.component.html',
  styleUrls: ['./placement-edit.component.scss']
})
export class PlacementEditComponent implements OnInit {

    public deleteIcon = faTrashAlt;
    public devicePlacements: DevicePlacement[];

    constructor(
        private deviceService: DeviceService,
        public dialogRef: MatDialogRef<PlacementEditComponent>,
        @Inject(MAT_DIALOG_DATA) public data: string) {
    }

    ngOnInit() {
        this.devicePlacements = this.deviceService.devicePlacements;
    }

    onCancelClick(): void {
        this.dialogRef.close();
    }
}
