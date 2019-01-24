import {Component, Inject, OnInit} from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';

@Component({
  selector: 'account-device-remove',
  templateUrl: './remove.component.html',
  styleUrls: ['./remove.component.scss']
})
export class RemoveComponent implements OnInit {

    constructor(
        public dialogRef: MatDialogRef<RemoveComponent>,
        @Inject(MAT_DIALOG_DATA) public data: boolean) {
    }

    ngOnInit() {
    }

    onCancelClick(): void {
        this.dialogRef.close();
    }
}
