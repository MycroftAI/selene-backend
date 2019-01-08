import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';

import { faTrashAlt } from '@fortawesome/free-solid-svg-icons';

import { DevicePlacement, DeviceService} from '../../device.service';

@Component({
    selector: 'account-device-geography',
    templateUrl: './geography-edit.component.html',
    styleUrls: ['./geography-edit.component.scss']
})
export class GeographyEditComponent implements OnInit {
    public deleteIcon = faTrashAlt;
    public deviceGeographies;

    constructor(
        private deviceService: DeviceService,
        public dialogRef: MatDialogRef<GeographyEditComponent>,
        @Inject(MAT_DIALOG_DATA) public data: string) {
    }

    ngOnInit() {
        this.deviceGeographies = this.deviceService.deviceGeographies;
    }

    onCancelClick(): void {
        this.dialogRef.close();
    }

}
