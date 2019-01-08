import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';

import { DeviceAttribute, DeviceService} from '../../device.service';

@Component({
    selector: 'account-device-group',
    templateUrl: './group-edit.component.html',
    styleUrls: ['./group-edit.component.scss']
})
export class GroupEditComponent implements OnInit {
    public deviceGroups: DeviceAttribute[];
    public dialogInstructions = 'Groups are useful to organize multiple ' +
        'devices.  You can reuse device names if they are in different groups.';

    constructor(
        private deviceService: DeviceService,
        public dialogRef: MatDialogRef<GroupEditComponent>,
        @Inject(MAT_DIALOG_DATA) public data: DeviceAttribute) {
    }

    ngOnInit() {
        this.deviceGroups = this.deviceService.deviceGroups;
    }
}
