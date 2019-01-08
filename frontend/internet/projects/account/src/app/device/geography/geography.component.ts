import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';

import { faTrashAlt } from '@fortawesome/free-solid-svg-icons';

import { DevicePlacement, DeviceService} from '../device.service';

@Component({
    selector: 'account-device-geography',
    templateUrl: './geography.component.html',
    styleUrls: ['./geography.component.scss']
})
export class GeographyComponent implements OnInit {
    public deleteIcon = faTrashAlt;
    public deviceGeographies;

    constructor(
        private deviceService: DeviceService,
        public dialogRef: MatDialogRef<GeographyComponent>,
        @Inject(MAT_DIALOG_DATA) public data: string) {
    }

    ngOnInit() {
        this.deviceGeographies = this.deviceService.deviceGeographies;
    }

    onCancelClick(): void {
        this.dialogRef.close();
    }

}
