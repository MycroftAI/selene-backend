import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';

import { DeviceAttribute, DeviceService} from '../../device.service';

@Component({
    selector: 'account-device-geography-edit',
    templateUrl: './geography-edit.component.html',
    styleUrls: ['./geography-edit.component.scss']
})
export class GeographyEditComponent implements OnInit {
    public deviceGeographies: DeviceAttribute[];
    public dialogInstructions = '';

    constructor(
        private deviceService: DeviceService,
        public dialogRef: MatDialogRef<GeographyEditComponent>,
        @Inject(MAT_DIALOG_DATA) public data: string) {
    }

    ngOnInit() {
        this.deviceGeographies = this.deviceService.deviceGeographies;
    }

}
