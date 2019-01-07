import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';

import { faTrashAlt } from '@fortawesome/free-solid-svg-icons';

import { DevicePlacement, DeviceService} from '../device.service';


@Component({
  selector: 'account-device-placement',
  templateUrl: './placement.component.html',
  styleUrls: ['./placement.component.scss']
})
export class PlacementComponent implements OnInit {

    public deleteIcon = faTrashAlt;
    public devicePlacements: DevicePlacement[];

    constructor(
        private deviceService: DeviceService,
        public dialogRef: MatDialogRef<PlacementComponent>,
        @Inject(MAT_DIALOG_DATA) public data: string) {
    }

    ngOnInit() {
        this.devicePlacements = this.deviceService.devicePlacements;
    }

    onCancelClick(): void {
        this.dialogRef.close();
    }
}
