import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';

import { DeviceAttribute, DeviceService} from '../../device.service';


@Component({
  selector: 'account-device-placement-edit',
  templateUrl: './placement-edit.component.html',
  styleUrls: ['./placement-edit.component.scss']
})
export class PlacementEditComponent implements OnInit {
    public devicePlacements: DeviceAttribute[];
    public dialogInstructions = 'You can optionally indicate where a device is ' +
        'placed within a location.  Field is informational only.';

    constructor(
        private deviceService: DeviceService,
        public dialogRef: MatDialogRef<PlacementEditComponent>,
        @Inject(MAT_DIALOG_DATA) public data: string) {
    }

    ngOnInit() {
        this.devicePlacements = this.deviceService.devicePlacements;
    }
}
