import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';

import { faTrashAlt } from '@fortawesome/free-solid-svg-icons';

import { DeviceGroup, DeviceService} from '../device.service';

@Component({
    selector: 'account-device-group',
    templateUrl: './device-group.component.html',
    styleUrls: ['./device-group.component.scss']
})
export class DeviceGroupComponent implements OnInit {
    public deleteIcon = faTrashAlt;
    public deviceGroups: DeviceGroup[];

    constructor(
        private deviceService: DeviceService,
        public dialogRef: MatDialogRef<DeviceGroupComponent>,
        @Inject(MAT_DIALOG_DATA) public data: DeviceGroup) {
    }

    ngOnInit() {
        this.deviceGroups = this.deviceService.deviceGroups;
    }

    onCancelClick(): void {
        this.dialogRef.close();
    }
}
