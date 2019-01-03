import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';

import { faTrashAlt } from '@fortawesome/free-solid-svg-icons';

import { DevicePlacement, DeviceService} from '../device.service';


@Component({
  selector: 'account-device-placement',
  templateUrl: './device-placement.component.html',
  styleUrls: ['./device-placement.component.scss']
})
export class DevicePlacementComponent implements OnInit {

    public deleteIcon = faTrashAlt;
    public devicePlacements: DevicePlacement[];
    public selectedPlacement: DevicePlacement;

    constructor(
        private deviceService: DeviceService,
        public dialogRef: MatDialogRef<DevicePlacementComponent>,
        @Inject(MAT_DIALOG_DATA) public data: DevicePlacement) {
    }

    ngOnInit() {
        this.devicePlacements = this.deviceService.devicePlacements;
        this.selectedPlacement = this.data;
    }

    onCancelClick(): void {
        this.dialogRef.close();
    }
}
