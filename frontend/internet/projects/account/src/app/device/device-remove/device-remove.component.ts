import {Component, Inject, OnInit} from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';

@Component({
  selector: 'account-device-remove',
  templateUrl: './device-remove.component.html',
  styleUrls: ['./device-remove.component.scss']
})
export class DeviceRemoveComponent implements OnInit {

    constructor(
        public dialogRef: MatDialogRef<DeviceRemoveComponent>,
        @Inject(MAT_DIALOG_DATA) public data: boolean) {
    }

    ngOnInit() {
    }

    onCancelClick(): void {
        this.dialogRef.close();
    }
}
