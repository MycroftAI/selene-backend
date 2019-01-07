import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';

import { faTrashAlt } from '@fortawesome/free-solid-svg-icons';

import { DeviceGroup, DeviceService} from '../device.service';

@Component({
    selector: 'account-device-group',
    templateUrl: './group.component.html',
    styleUrls: ['./group.component.scss']
})
export class GroupComponent implements OnInit {
    public deleteIcon = faTrashAlt;
    public deviceGroups: DeviceGroup[];

    constructor(
        private deviceService: DeviceService,
        public dialogRef: MatDialogRef<GroupComponent>,
        @Inject(MAT_DIALOG_DATA) public data: DeviceGroup) {
    }

    ngOnInit() {
        this.deviceGroups = this.deviceService.deviceGroups;
    }

    onCancelClick(): void {
        this.dialogRef.close();
    }
}
